"""
Utility functions used by the API
"""

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
