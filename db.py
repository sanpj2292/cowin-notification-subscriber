from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.schema import ForeignKey
from models import Subscriber
from typing import List
from sqlalchemy import Boolean, Column, Float, String, Integer, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite:///./.data/db.sqlite3?check_same_thread=False'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

# A SQLAlchemny ORM Subscribers
class DBSubscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), index=True)
    district_id = Column(Integer, default=581)
    state_id = Column(Integer, default=32)
    active = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now())
    
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

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_place(db: Session, email: str):
    return db.query(DBSubscriber).where(DBSubscriber.email == email).first()

# Methods for interacting with the database
def get_subscribers(db: Session) -> List[DBSubscriber]:
    return db.query(DBSubscriber).all()

def create_subscriber(db: Session, subscriber : Subscriber) -> DBSubscriber:
    db_subscriber = DBSubscriber(**subscriber.dict())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

def bulk_state_insert(db: Session, states: List[DBState]):
    db.bulk_save_objects(states, return_defaults=True)
    db.commit()

def bulk_district_insert(db: Session, districts: List[DBDistrict]):
    db.bulk_save_objects(districts, return_defaults=True)
    db.commit()

# Methods for interacting with the database
def get_states_all(db: Session) -> List[DBState]:
    return db.query(DBState).all()

def group_by_district(db: Session):
    subscribers_by_district = db.query(DBSubscriber.district_id, func.Count(DBSubscriber.district_id))\
            .group_by(DBSubscriber.district_id)
    return subscribers_by_district