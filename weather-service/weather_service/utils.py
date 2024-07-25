"""
Utility functions used by the API
"""

from datetime import datetime, timedelta
from functools import wraps
import os

from fastapi import HTTPException, Request
from weather_service.db_utils import insert_realtime_weather

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

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

def fetch_weather_data(api_url, city):
    response = requests.get(f"{api_url}?q={city}&appid={OPENWEATHER_API_KEY}")
    if response.status_code == 200:
        data = response.json()
        return {
            'dt': datetime.datetime.utcnow(),
            'rain': data.get('rain', {}).get('1h', 0),
            'snow': data.get('snow', {}).get('1h', 0),
            'clear': data.get('weather', [{}])[0].get('main', 'Clear'),
            'temp': data.get('main', {}).get('temp', 0),
            'feels_like': data.get('main', {}).get('feels_like', 0),
            'city': city
        }
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def insert_fetched_data(api_url, api_key, city):
    try:
        weather_data = fetch_weather_data(api_url, api_key, city)
        insert_realtime_weather(
            dt=weather_data['dt'],
            rain=weather_data['rain'],
            snow=weather_data['snow'],
            clear=weather_data['clear'],
            temp=weather_data['temp'],
            feels_like=weather_data['feels_like'],
            city=weather_data['city']
        )
    except Exception as e:
        print(f"Failed to insert data for {city}: {e}")

def hash_password(password):
    """
    Hashes the given password using SHA-256 algorithm
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

request_counts = {}
def rate_limit(limit: int, interval: int):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get the client IP address
            client_ip = request.client.host

            # Check if the IP is already in the dictionary
            if client_ip in request_counts:
                # Increment the request count for the IP
                request_counts[client_ip] += 1
            else:
                # Add the IP to the dictionary with initial count 1
                request_counts[client_ip] = 1

            # Check if the request count exceeds the limit
            if request_counts[client_ip] > limit:
                raise HTTPException(status_code=429, detail="Too many requests")

            # Call the actual endpoint function
            response = await func(request, *args, **kwargs)

            return response

        return wrapper

    return decorator