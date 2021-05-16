from fastapi import APIRouter, Request, Response, status
from fastapi.params import Body, Depends
from sqlalchemy.orm import Session
from models import Subscriber, SubscribeReqModel, SubscriberPincodeModel
from constants import LOC_BASE_URL, headers
from db import get_states_all, get_db, create_subscriber,\
    get_all_active_subscribers, delete_subscribers,insert_pincode_subscribers,\
    delete_pincode_subscribers, DBSubscriber
from typing import List
import requests
import json


router = APIRouter(
    prefix="/v2",
    tags=["v2"],
    responses={ 404: {"description": "Not found"} },
)

@router.get(path='/states')
def get_states():
    db = next(get_db())
    allStates = get_states_all(db)
    return {
        'states': allStates
    }

@router.get(path='/districts/{state_id}')
def get_cities(state_id: int):
    resp_dist = requests.get(f'{LOC_BASE_URL}/districts/{state_id}', headers=headers)
    resp_dist.raise_for_status()
    districts = json.loads(resp_dist.text)
    return {
        'districts': districts['districts'],
        'state_id': state_id
    }

@router.get('/subscriptions')
def get_subscriptions(email:str, DB:Session = Depends(get_db)):
    resp = get_all_active_subscribers(DB, email)
    return {
        'subscriptions': resp
    }

@router.delete('/subscribe')
def delete_subscribe(subscribers: List[Subscriber], DB:Session=Depends(get_db)):
    try:
        if delete_subscribers(DB, subscribers):
            return {
                'isError': False
            }
    except Exception as ex:
        return {
            'isError': True,
            'message': ex
        }


@router.post('/subscribe')
def subscribe(subscribeReqModel: SubscribeReqModel, response:Response, DB: Session = Depends(get_db)):
    try:
        subscriber = Subscriber(**subscribeReqModel.dict(), active=True)
        create_subscriber(DB, subscriber=subscriber)
        respDict = {
            'isSubscriptionSuccess': True,
        }
        response.status_code = status.HTTP_200_OK
    except Exception as inst:
        respDict = {
            'isSubscriptionSuccess': False,
            'error_message': inst
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    finally:
        return respDict


@router.delete('/pincode/subscribe')
def delete_subscribe(subscribers: List[SubscriberPincodeModel], DB:Session=Depends(get_db)):
    try:
        if delete_pincode_subscribers(DB, subscribers):
            return {
                'isError': False
            }
    except Exception as ex:
        return {
            'isError': True,
            'message': ex
        }

@router.post('/pincode/subscribe')
def pincode_subscribe(subscribers:List[SubscriberPincodeModel], DB:Session = Depends(get_db)):
    dbSubs = []
    try:
        for sub in subscribers:
            dbSubs.append(DBSubscriber(**sub.dict(), active=True))
        insert_pincode_subscribers(DB, dbSubs)
        return {
            'isError': True
        }
    except Exception as ex:
        print(ex)
        return {
            'isError': False,
            'message': ex
        }
