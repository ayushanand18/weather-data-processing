from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import datetime

from weather_service.db_models import engine, RealtimeWeather, DailyWeather, AlertEvent
import json

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
session = Session()

def cleanup_old_realtime_weather():
    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    session.query(RealtimeWeather).filter(RealtimeWeather.dt < cutoff_time).delete(synchronize_session=False)
    session.commit()

async def insert_realtime_weather(dt, main_condition, temp, feels_like, pressure, humidity, rain, clouds, city):
    # Clean up old records
    cleanup_old_realtime_weather()
    
    new_data = RealtimeWeather(
        dt=dt,
        main_condition=main_condition,
        temp=temp,
        feels_like=feels_like,
        pressure=pressure,
        humidity=humidity,
        rain=rain,
        clouds=clouds,
        city=city
    )
    session.add(new_data)
    session.commit()

def insert_daily_weather(date, avg_temp, max_temp, min_temp, dom_condition):
    new_data = DailyWeather(
        date=date,
        avg_temp=avg_temp,
        max_temp=max_temp,
        min_temp=min_temp,
        dom_condition=dom_condition
    )
    session.add(new_data)
    session.commit()

def insert_alert_event(dt, city, trigger, reason):
    new_event = AlertEvent(
        dt=dt,
        city=city,
        reason=reason,
        trigger=trigger,
    )
    session.add(new_event)
    session.commit()

def aggregate_daily_weather():
    today = datetime.date.today()
    start_time = datetime.datetime.combine(today, datetime.time.min)
    end_time = datetime.datetime.combine(today, datetime.time.max)
    
    result = session.query(
        RealtimeWeather.city,
        func.date(RealtimeWeather.dt).label('date'),
        func.avg(RealtimeWeather.temp).label('avg_temp'),
        func.max(RealtimeWeather.temp).label('max_temp'),
        func.min(RealtimeWeather.temp).label('min_temp'),
        func.max(RealtimeWeather.main_condition).label('dom_condition')
    ).filter(
        RealtimeWeather.dt >= start_time,
        RealtimeWeather.dt <= end_time
    ).group_by(
        RealtimeWeather.city,
        func.date(RealtimeWeather.dt)
    ).all()

    for row in result:
        
        daily_weather = DailyWeather(
            date=row.date,
            city=row.city,
            avg_temp=row.avg_temp,
            max_temp=row.max_temp,
            min_temp=row.min_temp,
            dom_condition=row.dom_condition
        )
        session.merge(daily_weather)
    
    session.commit()

def get_alerts():
    alerts = session.query(AlertEvent).all()
    return alerts

def get_historical_data():
    historical_data = session.query(DailyWeather).all()
    return json.dumps([data.__dict__ for data in historical_data])

def get_realtime_data():
    realtime_data = session.query(RealtimeWeather).all()
    data_list = [row.__dict__ for row in realtime_data]
        
    # Remove the SQLAlchemy internal properties
    for item in data_list:
        item.pop('_sa_instance_state', None)
    
    # Convert to JSON
    json_data = json.dumps(data_list, default=str)  # Use default=str to handle non-serializable fields like datetime
    
    return json_data