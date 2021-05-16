from sqlalchemy import create_engine
from sqlalchemy.orm import query, sessionmaker, Session
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.schema import ForeignKey
from models import Subscriber, SubscriberPincodeModel, SubscriberAllModel
from typing import List, Tuple
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
    search_type=Column(String(5), index=True, default="STDIS")
    pincode = Column(Integer)
    district_id = Column(Integer)
    state_id = Column(Integer)
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

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_place(db: Session, email: str):
    return db.query(DBSubscriber).filter(DBSubscriber.email == email).first()

# Methods for interacting with the database
def get_subscribers_by_district(db:Session, district_id:int):
    return db.query(DBSubscriber).filter(DBDistrict.district_id == district_id).all()

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

def get_all_active_subscribers(db:Session, email: str):
    activeSubscribers = db.query(DBState.state_name, DBDistrict.district_name, DBSubscriber)\
        .outerjoin(DBState, or_(DBState.state_id == DBSubscriber.state_id, DBSubscriber.state_id is None))\
        .outerjoin(DBDistrict,or_( DBDistrict.district_id == DBSubscriber.district_id, DBSubscriber.district_id is None ))\
        .filter(DBSubscriber.active == True)\
        .filter(DBSubscriber.email == email)\
        .all()
    
    subscribers = []
    for activeSubscriber in activeSubscribers:
        sub = SubscriberAllModel.from_orm(activeSubscriber['DBSubscriber'])
        subscribers.append({
            **sub.dict(),
            'state_name': activeSubscriber['state_name'],
            'district_name': activeSubscriber['district_name'],
        })
    return subscribers

def delete_subscribers(db:Session, subscribers:List[Subscriber]):
    email = subscribers[0].email
    db.begin()
    db.query(DBSubscriber)\
        .filter(DBSubscriber.email == email)\
        .filter(DBSubscriber.state_id.in_([sub.state_id for sub in subscribers]))\
        .filter(DBSubscriber.district_id.in_([sub.district_id for sub in subscribers]))\
        .delete()
    db.commit()
    return True


# Methods for interacting with the database
def get_states_all(db: Session) -> List[DBState]:
    return db.query(DBState).all()

def get_distinct_districts(db: Session) -> Tuple[int]:
    subscribers_by_district = db.query(DBSubscriber.district_id)\
            .distinct().all()
    subByDistList = list(zip(*subscribers_by_district))[0]
    return subByDistList

def get_district(db:Session, district:int) -> DBDistrict:
    return db.query(DBDistrict).filter(DBDistrict.district_id == district).first()

###### Pincode Subscription methods
def delete_pincode_subscribers(db:Session, subscribers:List[SubscriberPincodeModel]):
    email = subscribers[0].email
    db.begin()
    db.query(DBSubscriber)\
        .filter(DBSubscriber.email == email)\
        .filter(DBSubscriber.pincode.in_([sub.pincode for sub in subscribers]))\
        .delete()
    db.commit()
    return True

def insert_pincode_subscribers(db:Session, subscribers:List[DBSubscriber]):
    db.bulk_save_objects(subscribers, return_defaults=True)
    db.commit()