import requests
import json
import datetime
from constants import BASE_URL, headers
import os
import smtplib, ssl
from typing import List, Dict, Tuple
import time
from email.message import EmailMessage
from db import DBDistrict, get_db, get_district, get_distinct_districts, get_subscribers_by_district
import asyncio
from logger_app import get_logger

logger = get_logger(__name__, needFileHandler=True)

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

@background
def sendEmail(email: str, district_name: str):
    logger.info(f'Send Email {email} for {district_name} started')
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv('COWIN_EMAILER_EMAIL')
    password = os.getenv('COWIN_MAILER_PWD')
    message = EmailMessage()
    message.set_content('''
        Hi,
            This is an automated message from CoWin Notification Service
            Currently some windows are open for vaccination scheduling.
            Hurry up and book your slots.
        
        
        
        Note: Please do not reply to this mailer.''')
    message['Subject'] = f'Availability of slots to book in CoWin App: {district_name}'
    message['From'] = sender_email
    message['To'] = email
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())
        logger.info(f'Sent email to {email} for {district_name}')

def sendEmails(emails: List[str], district:DBDistrict, districtId:int, 
               prevAvailibilitySumDict: Dict[int, int], availabilitySum: int):
    for email in emails:
        if prevAvailibilitySumDict.get((email, districtId), 0) != availabilitySum:
            sendEmail(email, district.district_name)
            prevAvailibilitySumDict[(email, districtId)] = availabilitySum


def emailNotifier(dbGen, prevAvailibilitySumDict: Dict[int, int]):
    DB = next(dbGen)
    distintDistricts = get_distinct_districts(DB)
    for districtId in distintDistricts:
        availableSessions, availabilitySum = searchForAvailability(district=districtId)
        district = get_district(DB, district=districtId)
        subscribers = get_subscribers_by_district(DB, districtId)
        emails = [subscriber.email for subscriber in subscribers]
        logger.debug(f'Emails after query: {emails}')
        if len(availableSessions) > 0 :
            sendEmails(emails, district, districtId, prevAvailibilitySumDict, availabilitySum)

def notifyAvailabilityByEmail():
    prev = {}
    while True:
        emailNotifier(get_db(), prev)
        logger.info('Going to sleep...')
        time.sleep(30)

def searchForAvailability(district:int) -> Tuple[List[any], int]:
    logger.info('Availability Search begins')
    now = datetime.date.today()
    formattedNow = now.strftime("%d-%m-%Y")
    url = f'{BASE_URL}/sessions/public/findByDistrict?district_id={district}&date={formattedNow}'
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    availableSessions = []
    sessions = json.loads(resp.text)['sessions']
    availabilitySum = 0
    for session in sessions:
        if session['available_capacity'] > 0:
            availableSessions.append(session)
            availabilitySum += session['available_capacity']
    logger.info('Availability search ends')
    return (availableSessions, availabilitySum)