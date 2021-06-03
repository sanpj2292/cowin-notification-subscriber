from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy import Boolean, Column, Float, String, Integer, func, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
import datetime

# SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:{os.getenv("POSTGRES_ACCOUNT_PWD")}@localhost/cowin_subscribe'
Base = declarative_base()
# A SQLAlchemny ORM Subscribers
class DBSubscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), index=True)
    search_type=Column(String(5), index=True, default="STDIS")
    pincode = Column(Integer)
    min_age = Column(Integer, default=0)
    district_id = Column(Integer, ForeignKey('districts.district_id'))
    state_id = Column(Integer, ForeignKey('states.state_id'))
    active = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now())
    pushNotificationId = Column(BIGINT, ForeignKey('push_notifications.id'))
    
class DBState(Base):
    __tablename__ = "states"
    
    state_id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    state_name = Column(String(100), index=True)
    created_date = Column(DateTime, default=datetime.datetime.now())

class DBDistrict(Base):
    __tablename__ = 'districts'
    
    district_id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    state_id = Column(Integer, ForeignKey('states.state_id'), index=True)
    district_name = Column(String(100), index=True)
    created_date = Column(DateTime, default=datetime.datetime.now())

class DBPushNotification(Base):
    __tablename__ = 'push_notifications'
    id = Column(BIGINT, primary_key=True, index=True)
    endpoint = Column(Text, default='')
    expirationTime = Column(Float, default=None)
    created_date = Column(DateTime, default=datetime.datetime.now())
    p256dh = Column(Text, default='')
    auth = Column(Text, default='')