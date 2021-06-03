from fastapi import APIRouter, Request, Response, status
from fastapi.params import Body, Depends
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from models import Subscriber, SubscribeReqModel, SubscriberPincodeModel
from constants import LOC_BASE_URL, headers, VAPID_PRIVATE_KEY, VAPID_CLAIMS
from db import get_states_all, get_db, create_subscriber,\
    get_all_active_subscribers, delete_subscribers,insert_pincode_subscribers,\
    delete_pincode_subscribers, DBSubscriber
from background_task import notifyAvailabilityByEmail, notifyAvailabilityForStream, notifyAvailabilityV3
import os
from typing import List
import requests
import json
from logger_app import get_logger
from pywebpush import webpush, WebPushException

router = APIRouter(
    prefix="/api/v2",
    tags=["v2"],
    responses={ 404: {"description": "Not found"} },
)
__name__ = 'V2APIRouter'
logger = get_logger(__name__, needFileHandler=True)



def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )

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
        logger.info('Get Subscriptions method ends')
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
        logger.info('Subscribe method start -- hotreload check')
        subscriber = Subscriber(**subscribeReqModel.dict(exclude={'pushNotification'}), active=True)
        print('Notification details')
        print(subscribeReqModel.dict())
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
def delete_pincode_subscribe(subscribers: List[SubscriberPincodeModel], DB:Session=Depends(get_db)):
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
            dbSubs.append(DBSubscriber(**sub.dict(exclude={'pushNotification'}), active=True))
        isSuccess = insert_pincode_subscribers(DB, dbSubs)
        logKeyword = f'{"Uns" if not isSuccess else "S"}uccessfully'
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

# @router.get('/stream/subscriptions', response_class=StreamingResponse)
# def subscription_stream(email:str, DB:Session = Depends(get_db)):
#     try:
#         logger.info('Streaming going on')
#         return StreamingResponse(notifyAvailabilityForStream(email), headers={
#             'content-type': 'text/event-stream',
#             'Connection': 'keep-alive',
#             'X-Accel-Buffering': 'no'
#         })
#     except Exception as e:
#         logger.error('Streaming has exception')
#         logger.error(e)
#         return

@router.get('/stream/subscriptions')   
def subscription_stream(email:str):
    try:
        return notifyAvailabilityV3(email)
    except Exception as e:
        logger.error('Streaming has exception')
        logger.error(e)
        raise