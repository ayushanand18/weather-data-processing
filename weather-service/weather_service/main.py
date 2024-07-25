"""
API Contracts,
"""

import os
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI

from weather_service.db_utils import aggregate_daily_weather, check_password, get_alerts_for_user, get_user_id_from_email, insert_user, is_user_registered
from weather_service.utils import fetch_weather_data, hash_password, rate_limit
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta


app = FastAPI()

scheduler = BackgroundScheduler()


# Secret key to sign the JWT
SECRET_KEY = "your-secret-key"
# Algorithm used to sign the JWT
ALGORITHM = "HS256"
# Access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = 'https://api.openweathermap.org/data/2.5/weather'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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
        


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle Server Wake-up and shutdown"""
    scheduler.start()

    yield

    scheduler.shutdown()


###################
# API Endpoints

@app.get("/statistics")
@rate_limit(limit=5, interval=60)
async def statistics_combined_historical_and_realtime() :
    """
    Render Dashboard to view visualizations (combined).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass


@app.get("/statistics/realtime")
@rate_limit(limit=5, interval=60)
async def statistics_realtime() :
    """
    Render Dashboard to view visualizations (historical).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass

@app.get("/statistics/historical")
@rate_limit(limit=5, interval=60)
async def statistics_historical() :
    """
    Render Dashboard to view visualizations (realtime).
    """
    # utilise plotly/dash directly to render an interactive graph
    # this endpoint should not be authenticated
    # as users must get something to evaluate the results
    pass

@app.get("/alerts/json")
@rate_limit(limit=5, interval=60)
async def get_alerts_json(access_token: str):
    """Get JSON based alerts"""
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded_token.get("sub")
        alerts = get_alerts_for_user(user_id)
        return alerts
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/alerts/html")
@rate_limit(limit=5, interval=60)
async def get_alerts_html(access_token: str):
    """Get HTML based alerts"""
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded_token.get("sub")
        alerts = get_alerts_for_user(user_id)

        # Convert alerts to HTML table
        table_html = "<table>"
        table_html += "<tr><th>Alert ID</th><th>Reason</th><th>Timestamp</th></tr>"
        for alert in alerts:
            table_html += f"<tr><td>{alert['alert_id']}</td><td>{alert['reason']}</td><td>{alert['dt']}</td></tr>"
        table_html += "</table>"

        return table_html
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def authenticate_user(email_id: str, password: str):
    # Hash the password (you can use your preferred hashing algorithm)
    hashed_password = hash_password(password)

    # Check if the user is registered and the password is correct
    if not is_user_registered(email_id):
        return False
    if not check_password(email_id, hashed_password):
        return False

    return True

async def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/auth/login")
@rate_limit(limit=5, interval=60)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email_id = form_data.username
    password = form_data.password

    # Authenticate the user
    if not await authenticate_user(email_id, password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Get the user_id from the User table based on the email_id
    user_id = get_user_id_from_email(email_id)
    access_token = await create_access_token({"sub": user_id}, access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register")
@rate_limit(limit=5, interval=60)
async def signup(email_id: str, password: str):
    """Register a new user and save their credentials"""
    # Perform validation checks on email_id and password
    if len(email_id) < 6:
        raise HTTPException(status_code=400, detail="User ID must be at least 6 characters long")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    if not any(char.isdigit() or not char.isalpha() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least 1 number or special character")

    # Hash the password (you can use your preferred hashing algorithm)
    hashed_password = hash_password(password)

    # Check if the user is already registered
    if is_user_registered(email_id):
        raise HTTPException(status_code=400, detail="User ID is already registered")

    # Insert the user into the database
    insert_user(email_id, hashed_password)

    return {"message": "User registered successfully"}
