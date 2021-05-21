from sqlalchemy import create_engine
from sqlalchemy.orm import query, sessionmaker, Session
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.sql.schema import ForeignKey
from models import Subscriber, SubscriberPincodeModel, SubscriberAllModel
from typing import List, Tuple, Union
from sqlalchemy import Boolean, Column, Float, String, Integer, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy_utils.functions import database_exists, create_database
import os

# SqlAlchemy Setup
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./.data/db.sqlite3?check_same_thread=False'
# SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:{os.getenv("POSTGRES_ACCOUNT_PWD")}@localhost/cowin_subscribe'
Base = declarative_base()

# A SQLAlchemny ORM Subscribers
class DBSubscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), index=True)
    search_type=Column(String(5), index=True, default="STDIS")
    pincode = Column(Integer)
    district_id = Column(Integer, ForeignKey('districts.district_id'))
    state_id = Column(Integer, ForeignKey('states.state_id'))
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

if __name__ == '__main__':
    SQLALCHEMY_DATABASE_URL = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:5432/cowin_subscribe'
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    if not database_exists(engine.url):
        create_database(engine.url)
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
    return db.query(DBSubscriber).filter(DBDistrict.district_id == district_id)\
        .distinct(DBSubscriber.district_id, DBSubscriber.email).all()

def get_subscribers(db: Session) -> List[DBSubscriber]:
    return db.query(DBSubscriber).all()

def create_subscriber(db: Session, subscriber : Subscriber) -> DBSubscriber:
    db_subscriber = DBSubscriber(**subscriber.dict(), search_type="STDIS")
    if check_subscription(db, [db_subscriber]):
        db.add(db_subscriber)
        db.commit()
        db.refresh(db_subscriber)
        return True
    else:
        return False

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
    data = db.query(DBSubscriber)\
        .filter(DBSubscriber.email == email)\
        .filter(DBSubscriber.state_id.in_([sub.state_id for sub in subscribers]))\
        .filter(DBSubscriber.district_id.in_([sub.district_id for sub in subscribers]))\
        .delete()
    db.commit()
    return data > 0


# Methods for interacting with the database
def get_states_all(db: Session) -> List[DBState]:
    return db.query(DBState).all()

def get_distinct_districts(db: Session) -> Tuple[int]:
    subscribers_by_district = db.query(DBSubscriber.district_id)\
            .filter(DBSubscriber.district_id.isnot(None))\
            .distinct().all()
    subByDistList = list(zip(*subscribers_by_district))[0]
    return subByDistList

def get_district(db:Session, district:int) -> DBDistrict:
    return db.query(DBDistrict).filter(DBDistrict.district_id == district).first()

def get_dis_state_nm(db:Session, district_id:int):
    return db.query(DBDistrict.district_name, DBState.state_name)\
        .join(DBState, DBState.state_id == DBDistrict.state_id)\
        .filter(DBDistrict.district_id == district_id).first()

###### Pincode Subscription methods
def delete_pincode_subscribers(db:Session, subscribers:List[SubscriberPincodeModel]):
    email = subscribers[0].email
    db.begin()
    data = db.query(DBSubscriber)\
        .filter(DBSubscriber.email == email)\
        .filter(DBSubscriber.pincode.in_([sub.pincode for sub in subscribers]))\
        .delete()
    db.commit()
    return data > 0

def insert_pincode_subscribers(db:Session, subscribers:List[DBSubscriber]):
    if check_subscription(db, subscribers):
        db.bulk_save_objects(subscribers, return_defaults=True)
        db.commit()
        return True
    else:
        return False
    
def check_subscription(db: Session, subscribers: List[DBSubscriber]):
    if len(subscribers)> 0:
        email = subscribers[0].email
        search_type = subscribers[0].search_type
        data = None
        emailFilter = db.query(DBSubscriber)\
                .filter(DBSubscriber.email == email)
        if search_type == "STDIS":
            data = emailFilter\
                .filter(DBSubscriber.state_id.in_([sub.state_id for sub in subscribers]))\
                .filter(DBSubscriber.district_id.in_([sub.district_id for sub in subscribers]))
        elif search_type == "PINCD":
            data = emailFilter\
                .filter(DBSubscriber.pincode.in_([sub.pincode for sub in subscribers]))
        else:
            raise Exception('Search Type is wrong')
        return data is None or data.count() == 0
    else:
        raise Exception('Input is wrong')