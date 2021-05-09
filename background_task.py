import requests
import json
import datetime
from constants import BASE_URL, DISTRICT_ID, headers
import os
import smtplib, ssl
from typing import List
import time
from email.message import EmailMessage
from db import get_db, get_subscribers, group_by_district
from concurrent.futures import ThreadPoolExecutor
import asyncio

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

def sendEmails(emails: List[str]):
    print('In SendEmails func....')
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv('COWIN_EMAILER_EMAIL')
    receivers_email = ','.join(emails)
    password = os.getenv('COWIN_MAILER_PWD')
    message = EmailMessage()
    message.set_content('''
        Hi,
            This is an automated message from CoWin Notification Service
            Currently some windows are open for vaccination scheduling.
            Hurry up and book your slots.
        
        
        
        Note: Please do not reply to this mailer.''')
    message['Subject'] = 'Availability of slots to book in CoWin App'
    message['From'] = sender_email
    message['To'] = receivers_email
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receivers_email, message.as_string())
    print('Done SendEmails func....')

@background
def notifyAvailabilityByEmail():
    while True:
        database = get_db()
        groupByDistrict = group_by_district(next(database))
        availableSessions = searchForAvailability()
        if len(availableSessions) > 0:
            print('Fetching emails')
            database = get_db()
            subscribers = get_subscribers(next(database))
            emails = [subscriber.email for subscriber in subscribers]
            sendEmails(emails)
        print('Just before sleep')
        time.sleep(30)
        # if os.path.exists(os.path.dirname(DATAFILENAME)):
        #     with open(DATAFILENAME, 'r') as file:
        #         emails = file.read().strip().split(' ')
                

def searchForAvailability():
    print('In searchForAvailability...')
    now = datetime.date.today()
    formattedNow = now.strftime("%d-%m-%Y")
    url = f'{BASE_URL}/sessions/public/findByDistrict?district_id={DISTRICT_ID}&date={formattedNow}'
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    availableSessions = []
    sessions = json.loads(resp.text)['sessions']
    for session in sessions:
        if session['available_capacity'] > 0:
            availableSessions.append(session)
    print('Done with searchForAvailability...')
    return availableSessions