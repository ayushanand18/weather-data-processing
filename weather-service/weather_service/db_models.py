from sqlalchemy import create_engine, Column, String, Date, Numeric, Boolean, ForeignKey, UniqueConstraint, Table, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

# Fetching database connection details from environment variables
DB_USER = os.getenv('DB_USER', 'default_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')

Base = declarative_base()

class RealtimeWeather(Base):
    __tablename__ = 'realtime_weather'
    
    dt = Column(TIMESTAMP, unique=True, nullable=False, primary_key=True)
    city = Column(String, nullable=False, primary_key=True)
    rain = Column(Numeric, nullable=False)
    snow = Column(Numeric, nullable=False)
    clear = Column(Numeric, nullable=False)
    temp = Column(Numeric, nullable=False)
    feels_like = Column(Numeric, nullable=False)

class DailyWeather(Base):
    __tablename__ = 'daily_weather'
    
    date = Column(Date, primary_key=True)
    city = Column(String, primary_key=True)
    avg_temp = Column(Numeric, nullable=False)
    max_temp = Column(Numeric, nullable=False)
    min_temp = Column(Numeric, nullable=False)
    dom_condition = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

class UserAlert(Base):
    __tablename__ = 'user_alerts'
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    field = Column(String, nullable=False)
    threshold = Column(Numeric, nullable=False)
    disabled = Column(Boolean, nullable=False, default=True)

class AlertEvent(Base):
    __tablename__ = 'alert_events'
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dt = Column(TIMESTAMP, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    reason = Column(String, nullable=False)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('user_alerts.alert_id'), nullable=False)

# Create an engine
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)
