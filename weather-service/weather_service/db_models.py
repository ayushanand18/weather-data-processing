import os
from sqlalchemy import create_engine, Column, String, Date, Numeric, Boolean, ForeignKey, UniqueConstraint, Table, TIMESTAMP, inspect, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from dotenv import load_dotenv

load_dotenv()

# Fetching database connection details from environment variables
DB_USER = os.getenv('DB_USER', 'default_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')

Base = declarative_base()

class RealtimeWeather(Base):
    __tablename__ = 'realtime_weather'
    
    dt = Column(TIMESTAMP, nullable=False, primary_key=True)
    main_condition = Column(String, nullable=False)
    temp = Column(Numeric, nullable=False)
    feels_like = Column(Numeric, nullable=False)
    pressure = Column(Numeric, nullable=False)
    humidity = Column(Numeric, nullable=False)
    rain = Column(Numeric, nullable=False)
    clouds = Column(Numeric, nullable=False)
    city = Column(String, nullable=False, primary_key=True)


class DailyWeather(Base):
    __tablename__ = 'daily_weather'
    
    date = Column(Date, primary_key=True)
    city = Column(String, primary_key=True)
    avg_temp = Column(Numeric, nullable=False)
    max_temp = Column(Numeric, nullable=False)
    min_temp = Column(Numeric, nullable=False)
    dom_condition = Column(String, nullable=False)


class AlertEvent(Base):
    __tablename__ = 'alert_events'
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dt = Column(TIMESTAMP, nullable=False)
    city=Column(String, nullable=False)
    reason = Column(String, nullable=False)
    trigger = Column(String, nullable=False)

# Create an engine
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)
