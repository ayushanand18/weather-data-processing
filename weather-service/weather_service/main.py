"""
API Contracts,
"""

from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler


app = FastAPI()

scheduler = BackgroundScheduler()


CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = os.getenv('OPENWEATHER_API_KEY')


@scheduler.scheduled_job('cron', hour=0, minute=1)
def scheduled_job():
    aggregate_daily_weather()


@scheduler.scheduled_job('interval', minutes=5)
def fetch_and_insert_data():
    for city in CITIES:
        try:
            fetch_weather_data(API_URL, city)
        except Exception as e:
            print(f"Failed to insert data for {city}: {e}")
        
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.get("/statistics")
async def statistics_combined_historical_and_realtime(request: Request) :
    """
    Render Dashboard to view visualizations (combined).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass

@app.get("/statistics/realtime")
async def statistics_realtime(request: Request) :
    """
    Render Dashboard to view visualizations (historical).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass

@app.get("/statistics/historical")
async def statistics_historical(request: Request) :
    """
    Render Dashboard to view visualizations (realtime).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass

@app.get("/alerts/json")
async def get_alerts_json(access_token: str):
    """Get JSON based alerts"""
    pass

@app.get("/alerts/html")
async def get_alerts_html(access_token: str):
    """Get HTML based alerts"""
    pass

@app.get("/auth/login")
async def login():
    """Login the user, and present JWT for access"""
    pass

@app.get("/auth/register")
async def signup():
    """register a new user, and save its credentials"""
    pass
