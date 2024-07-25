from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import datetime

from weather_service.db_models import engine, RealtimeWeather, DailyWeather, User, UserAlert, AlertEvent

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

def cleanup_old_realtime_weather():
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    session.query(RealtimeWeather).filter(RealtimeWeather.dt < cutoff_time).delete(synchronize_session=False)
    session.commit()

def insert_realtime_weather(dt, rain, snow, clear, temp, feels_like, city):
    # Clean up old records
    cleanup_old_realtime_weather()
    
    new_data = RealtimeWeather(
        dt=dt,
        rain=rain,
        snow=snow,
        clear=clear,
        temp=temp,
        feels_like=feels_like,
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

def insert_user(email, password):
    new_user = User(
        email=email,
        password=password,
    )
    session.add(new_user)
    session.commit()

def insert_user_alert(user_id, field, threshold, disabled=True):
    new_alert = UserAlert(
        user_id=user_id,
        field=field,
        threshold=threshold,
        disabled=disabled
    )
    session.add(new_alert)
    session.commit()

def insert_alert_event(dt, user_id, reason, alert_id):
    new_event = AlertEvent(
        dt=dt,
        user_id=user_id,
        reason=reason,
        alert_id=alert_id
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
        func.sum(RealtimeWeather.rain).label('total_rain'),
        func.sum(RealtimeWeather.snow).label('total_snow'),
        func.sum(RealtimeWeather.clear).label('total_clear')
    ).filter(
        RealtimeWeather.dt >= start_time,
        RealtimeWeather.dt <= end_time
    ).group_by(
        RealtimeWeather.city,
        func.date(RealtimeWeather.dt)
    ).all()

    for row in result:
        if row.total_rain >= row.total_snow and row.total_rain >= row.total_clear:
            dom_condition = 'Rain'
        elif row.total_snow >= row.total_rain and row.total_snow >= row.total_clear:
            dom_condition = 'Snow'
        else:
            dom_condition = 'Clear'

        daily_weather = DailyWeather(
            date=row.date,
            city=row.city,
            avg_temp=row.avg_temp,
            max_temp=row.max_temp,
            min_temp=row.min_temp,
            dom_condition=dom_condition
        )
        session.merge(daily_weather)
    
    session.commit()

def is_user_registered(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    return user is not None

def check_password(email, hashed_password):
    user = session.query(User).filter(User.email == email, User.password == hashed_password).first()
    return user is not None

def get_user_id_from_email(email):
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user.id
    else:
        return None
    
def get_alerts_for_user(user_id):
    alerts = session.query(AlertEvent).filter(AlertEvent.user_id == user_id).all()
    return alerts