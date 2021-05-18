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
from logger_app import get_logger


router = APIRouter(
    prefix="/v2",
    tags=["v2"],
    responses={ 404: {"description": "Not found"} },
)
__name__ = 'V2APIRouter'
logger = get_logger(__name__, needFileHandler=True)

@router.get(path='/states')
def get_states():
    try:
        logger.info('Get States method start')
        db = next(get_db())
        allStates = get_states_all(db)
        logger.info('Get States method succesfully ends')
        return {
            'states': allStates
        }
    except Exception as e:
        logger.error('Get States method error:')
        logger.error(e)

@router.get(path='/districts/{state_id}')
def get_cities(state_id: int):
    try:
        logger.info('Get Districts method start')
        resp_dist = requests.get(f'{LOC_BASE_URL}/districts/{state_id}', headers=headers)
        resp_dist.raise_for_status()
        districts = json.loads(resp_dist.text)
        logger.info('Get Districts method successfully ends')
        return {
            'districts': districts['districts'],
            'state_id': state_id
        }
    except Exception as e:
        logger.error('Get Districts method error:')
        logger.error(e)

@router.get('/subscriptions')
def get_subscriptions(email:str, DB:Session = Depends(get_db)):
    try:
        logger.info('Get Subscriptions method start')
        resp = get_all_active_subscribers(DB, email)
        return {
            'subscriptions': resp
        }
    except Exception as e:
        logger.error('Get Subscriptions method error:')
        logger.error(e)
        

@router.delete('/subscribe')
def delete_subscribe(subscribers: List[Subscriber], DB:Session=Depends(get_db)):
    try:
        logger.info('Delete Subscriptions method start')
        if delete_subscribers(DB, subscribers):
            logger.info('Delete Subscriptions method successfully ends')
            return {
                'isError': False
            }
        else:
            logger.info('Delete Subscriptions method unsuccessfully ends')
            return {
                'isError': True,
                'message': 'Cannot be deleted'
            }
    except Exception as ex:
        logger.info('Delete Subscriptions method error:')
        logger.info(ex)
        return {
            'isError': True,
            'message': ex
        }


@router.post('/subscribe')
def subscribe(subscribeReqModel: SubscribeReqModel, response:Response, DB: Session = Depends(get_db)):
    try:
        logger.info('Subscribe method start')
        subscriber = Subscriber(**subscribeReqModel.dict(), active=True)
        isSuccess = create_subscriber(DB, subscriber=subscriber)
        respDict = {
            'isSubscriptionSuccess': isSuccess,
        }
        response.status_code = status.HTTP_200_OK
        logger.info('Subscribe method successfully ends')
    except Exception as inst:
        respDict = {
            'isSubscriptionSuccess': False,
            'error_message': inst
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.info('Subscribe method error:')
        logger.info(inst)
    finally:
        return respDict


@router.delete('/pincode/subscribe')
def delete_subscribe(subscribers: List[SubscriberPincodeModel], DB:Session=Depends(get_db)):
    try:
        logger.info('Delete Pincode Subscriptions method start')
        if delete_pincode_subscribers(DB, subscribers):
            logger.info('Delete Pincode Subscriptions method successfully ends')
            return {
                'isError': False
            }
        else:
            logger.info('Delete Pincode Subscriptions method unsuccessfully ends')
            return {
                'isError': True
            }
    except Exception as ex:
        logger.info('Delete Pincode Subscriptions method error:')
        logger.info(ex)
        return {
            'isError': True,
            'message': ex
        }

@router.post('/pincode/subscribe')
def pincode_subscribe(subscribers:List[SubscriberPincodeModel], DB:Session = Depends(get_db)):
    dbSubs = []
    try:
        logger.info('Pincode Subscribe method start')
        for sub in subscribers:
            dbSubs.append(DBSubscriber(**sub.dict(), active=True))
        isSuccess = insert_pincode_subscribers(DB, dbSubs)
        logKeyword = f'{"un" if not isSuccess else ""}successfully'
        logger.info(f'Pincode Subscribe method {logKeyword} ends')
        return {
            'isSubscriptionSuccess': isSuccess
        }
    except Exception as ex:
        logger.info('Pincode Subscribe method error:')
        logger.info(ex)
        return {
            'isSubscriptionSuccess': False,
            'message': ex
        }
