"""
API Contracts,
"""

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logging

from fastapi.responses import HTMLResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from weather_service.db_utils import aggregate_daily_weather, get_alerts
from weather_service.utils import check_data_against_alerts, fetch_weather_data, insert_fetched_data, rate_limit, thresholds
from fastapi import HTTPException
from dotenv import load_dotenv
from weather_service.dash_app_statistics import app as dash_app_statistics
from weather_service.dash_app_threshold import app as dash_app_threshold
from weather_service.dash_app_alerts import app as dash_app_alerts

load_dotenv()
logging.basicConfig(format='%(asctime)s %(user)-8s %(message)s')


scheduler = AsyncIOScheduler()


CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')



def scheduled_job():
    aggregate_daily_weather()

async def fetch_and_insert_data():
    logging.info("Fetching and inserting data realtime.")
    for city in CITIES:
        try:
            
            weather_data = await fetch_weather_data(API_URL, OPENWEATHER_API_KEY, city)
            await insert_fetched_data(weather_data)
            await check_data_against_alerts(weather_data, thresholds.get_thresholds())
            print("Fetching data")
        except Exception as e:
            print(f"Failed to insert data for {city}: {e}")
        

scheduler.add_job(aggregate_daily_weather, 'cron', hour=0, minute=1)
scheduler.add_job(fetch_and_insert_data, IntervalTrigger(seconds=30))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle Server Wake-up and shutdown"""
    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

###################
# API Endpoints


app.mount("/statistics", WSGIMiddleware(dash_app_statistics.server))
app.mount("/configs", WSGIMiddleware(dash_app_threshold.server))
app.mount("/alerts", WSGIMiddleware(dash_app_alerts.server))

@app.get("/")
@rate_limit(limit=5, interval=60)
async def hello(request: Request):
    return {"status": "ok"}


@app.get("/alerts/json")
@rate_limit(limit=5, interval=60)
async def get_alerts_json(request: Request):
    """Get JSON based alerts"""
    try:
        alerts = get_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=401, detail=getattr(e, 'message', repr(e)))

@app.get("/alerts/html")
@rate_limit(limit=5, interval=60)
async def get_alerts_html(request: Request):
    """Get HTML based alerts"""
    try:
        alerts = get_alerts()

        # Convert alerts to HTML table
        table_html = "<table>"
        table_html += "<tr><th>Alert ID</th><th>Timestamp</th><th>City</th><th>Reason</th><th>Trigger</th></tr>"
        for alert in alerts:
            table_html += f"<tr>\
            <td>{alert.event_id}</td>\
            <td>{alert.dt}</td>\
            <td>{alert.city}</td>\
            <td>{alert.reason}</td>\
            <td>{alert.trigger}</td></tr>"
        table_html += "</table>"

        return HTMLResponse(table_html)
    except Exception as e:
        raise HTTPException(status_code=401, detail=getattr(e, 'message', repr(e)))
