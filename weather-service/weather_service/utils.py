"""
Utility functions used by the API
"""

from datetime import datetime, timedelta
from time import time
from functools import wraps
from typing import Dict

from fastapi import HTTPException, Request
from weather_service.db_utils import insert_alert_event, insert_realtime_weather


def cache_with_timeout(timeout):
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            if key in cache and datetime.now() - cache[key]['timestamp'] < timedelta(seconds=timeout):
                return cache[key]['value']
            else:
                result = func(*args, **kwargs)
                cache[key] = {'value': result, 'timestamp': datetime.utcnow()}
                return result
        return wrapper
    return decorator

@cache_with_timeout('1 day')
def fetch_aggregate_data_from_db():
    """
    Fetch aggregate weather data from db for visualization
    """

    # fetch the data from db around temperature, weather conditions
    # etc over the days, like past 30 days, past 1 month, etc
    # if a standard filter is used, cache the request with a TTL = 1 day
    pass

@cache_with_timeout('5 mins')
def fetch_realtime_data_from_db():
    """
    Fetch realtime weather data from db for visualization
    """
    # fetch the data from db and cache for 5 mins, as ping duration is
    # around 5 mins, so before that data is not going to be updated
    # opted not to update directy from the pooling service to a common
    # data structure, because your servers must be stateless (REST)
    pass

def dump_realtime_data_to_db():
    """
    Dump realtime data to the database
    """
    # perform validation checks, and output exceptions as suited
    # dump all of this data to a database
    pass

def cron_job_perform_aggregation():
    """
    Perform aggregation on past day's data and dump to database
    """
    # do not make a stored procedure, but aggregate rather in the code
    # so that it goes through code review, and any data change gets reviewed
    # schedule at 12 : 00 everyday
    pass

import requests
import hashlib

def get_lat_lon_for_city(city, api_key):
    """
    Get latitude and longitude for a given city
    """
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city},{91}&limit={1}&appid={api_key}")
    if response.status_code == 200:
        data = response.json()[0]
        return data.get('lat'), data.get('lon')
    else:
        raise Exception(f"API request failed with status code {response.status_code}")             

async def fetch_weather_data(api_url, api_key, city):
    lat, lon = get_lat_lon_for_city(city, api_key)
    response = requests.get(f"{api_url}?lat={lat}&lon={lon}&appid={api_key}")
    if response.status_code == 200:
        data = response.json()
        result = {
            'dt': datetime.fromtimestamp(data['dt']),
            'main_condition': data['weather'][0]['main'],
            'temp': data['main']['temp'] - 273.15,
            'feels_like': data['main']['feels_like'] - 273.15,
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'rain': data.get('rain', {}).get('1h', 0),
            'clouds': data['clouds'].get('all', 0),
            'city': city,
        }
        return result
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


async def insert_fetched_data(weather_data):
    try:
        await insert_realtime_weather(
            dt=weather_data['dt'],
            main_condition=weather_data['main_condition'],
            pressure=weather_data['pressure'],
            humidity=weather_data['humidity'],
            clouds=weather_data['clouds'],
            rain=weather_data['rain'],
            temp=weather_data['temp'],
            feels_like=weather_data['feels_like'],
            city=weather_data['city']
        )
    except Exception as e:
        print(f"Failed to insert data for {weather_data['city']}: {e}")

def hash_password(password):
    """
    Hashes the given password using SHA-256 algorithm
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

request_counts: Dict[str, Dict[str, int]] = {}

def rate_limit(limit: int, interval: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time()

            if client_ip not in request_counts:
                request_counts[client_ip] = {"count": 0, "timestamp": current_time}
            
            request_info = request_counts[client_ip]
            
            # Reset the count if the interval has passed
            if current_time - request_info["timestamp"] > interval:
                request_info["count"] = 0
                request_info["timestamp"] = current_time
            
            # Increment the request count
            request_info["count"] += 1
            
            # Check if the request count exceeds the limit
            if request_info["count"] > limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def check_data_against_alerts(weather_data, thresholds):
    """
    Check if weather data parameters are over user-defined thresholds
    """

    # Check if temperature exceeds threshold
    if weather_data['temp'] < thresholds['temp'][0] or weather_data['temp'] > thresholds['temp'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Temperature', f'Found temp: {weather_data["temp"]} but threshold is {thresholds["temp"]}')
        print(f"Temperature threshold exceeded for {weather_data['city']}")
    
    # Check if feels_like exceeds threshold
    if weather_data['feels_like'] < thresholds['feels_like'][0] or weather_data['feels_like'] > thresholds['feels_like'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Feels Like', f'Found feels like: {weather_data["feels_like"]} but threshold is {thresholds["feels_like"]}')
        print(f"Feels like threshold exceeded for {weather_data['city']}")

    # Check if pressure exceeds threshold
    if weather_data['pressure'] < thresholds['pressure'][0] or weather_data['pressure'] > thresholds['pressure'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Pressure', f'Found pressure: {weather_data["pressure"]} but threshold is {thresholds["pressure"]}')
        print(f"Pressure threshold exceeded for {weather_data['city']}")

    # Check if humidity exceeds threshold
    if weather_data['humidity'] < thresholds['humidity'][0] or weather_data['humidity'] > thresholds['humidity'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Humidity', f'Found humidity: {weather_data["humidity"]} but threshold is {thresholds["humidity"]}')
        print(f"Humidity threshold exceeded for {weather_data['city']}")

    # Check if rain exceeds threshold
    if weather_data['rain'] < thresholds['rain'][0] or weather_data['rain'] > thresholds['rain'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Rain', f'Found rain: {weather_data["rain"]} but threshold is {thresholds["rain"]}')
        print(f"Rain threshold exceeded for {weather_data['city']}")

    # Check if clouds exceeds threshold
    if weather_data['clouds'] < thresholds['clouds'][0] or weather_data['clouds'] > thresholds['clouds'][1]:
        insert_alert_event(weather_data['dt'], weather_data['city'], 'Clouds', f'Found clouds: {weather_data["clouds"]} but threshold is {thresholds["clouds"]}')
        print(f"Clouds threshold exceeded for {weather_data['city']}")

class Thresholds:
    def __init__(self, temp, feels_like, pressure, humidity, rain, clouds):
        self.temp = temp
        self.feels_like = feels_like
        self.pressure = pressure
        self.humidity = humidity
        self.rain = rain
        self.clouds = clouds
    
    def get_thresholds(self):
        return {
            'temp': self.temp,
            'feels_like': self.feels_like,
            'pressure': self.pressure,
            'humidity': self.humidity,
            'rain': self.rain,
            'clouds': self.clouds,
        }
    
    def update_thresholds(self, temp, feels_like, pressure, humidity, rain, clouds):
        self.temp = temp
        self.feels_like = feels_like 
        self.pressure = pressure 
        self.humidity = humidity
        self.rain = rain
        self.clouds = clouds

thresholds = Thresholds(temp=[0, 100], feels_like=[0, 100], pressure=[0, 1000], humidity=[0, 100], rain=[0, 100], clouds=[0, 100])