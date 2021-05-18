import requests
import json
import datetime
from constants import BASE_URL, headers
import os
import smtplib, ssl
from typing import List, Dict, Tuple
import time
from email.message import EmailMessage, MIMEPart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db import DBDistrict, get_db, get_district, get_distinct_districts, get_subscribers_by_district\
    , get_subscribers, get_dis_state_nm
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
        availableSessions, availabilitySum = searchForAvailability(param=districtId)
        district = get_district(DB, district=districtId)
        subscribers = get_subscribers_by_district(DB, districtId)
        emails = [subscriber.email for subscriber in subscribers]
        logger.debug(f'Emails after query: {emails}')
        if len(availableSessions) > 0 :
            sendEmails(emails, district, districtId, prevAvailibilitySumDict, availabilitySum)
            

def notifyAvailabilityByEmail():
    prev = {}
    while True:
        try:
            # emailNotifier(get_db(), prev)
            emailDataDict = emailNotifierV2(get_db(), prev)
            emailContentDict = prepareEmailContent(emailDataDict)
            
            sendEmailV2(emailContentDict)
            logger.info('Going to sleep...')
            time.sleep(30)
        except Exception as ex:
            logger.error(ex)

def searchForAvailability(param:int, code:str="STDIS") -> Tuple[List[any], int]:
    logger.info('Availability Search begins')
    now = datetime.date.today()
    formattedNow = now.strftime("%d-%m-%Y")
    endpoint = "findByDistrict"
    queryParam = f"district_id={param}"
    if code == "PINCD":
        endpoint = "findByPin"
        queryParam = f"pincode={param}"
    url = f'{BASE_URL}/sessions/public/{endpoint}?{queryParam}&date={formattedNow}'
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    availableSessions = []
    sessions = json.loads(resp.text).get('sessions', [])
    availabilitySum = 0
    for session in sessions:
        if session['available_capacity'] > 0:
            availableSessions.append(session)
            availabilitySum += session['available_capacity']
    logger.info('Availability search ends')
    return (availableSessions, availabilitySum)

def emailNotifierV2(dbGen, prevAvailabilitySumDict: Dict[str, Dict[str, Dict[int, int]]]):
    DB = next(dbGen)
    dbSubs = get_subscribers(DB)
    visited_params = {} # to check for visited pincode/district
    dataCollectDict = {}
    for dbSub in dbSubs:
        searchType = dbSub.search_type
        isDistrict = dbSub.search_type == "STDIS"
        param = dbSub.district_id if isDistrict else dbSub.pincode
        
        email = dbSub.email
        logger.debug(f'Email: {email}')
        if (visited_params.get(searchType) is None or 
            (visited_params.get(searchType) is not None and 
             visited_params[searchType].get(param) is None)):
            
            # requesting data from a district or pincode for the first time
            availSessions, availSum = searchForAvailability(param, dbSub.search_type)
            visited_params[searchType] = { **visited_params.get(searchType, {}), **dict(zip([param], [(availSessions, availSum)])) }
        # Condition to check available and to also check prevAvailability with current one
        if len(visited_params[searchType][param][0]) > 0:
            sT = {} 
            pD = {}
            availableSum = visited_params[searchType][param][1]
            
            pD[param] = visited_params[searchType][param][1]
            sT[searchType] = pD
            # if (
            #     email not in prevAvailabilitySumDict or 
            #     searchType not in prevAvailabilitySumDict[email] or 
            #     param not in prevAvailabilitySumDict[email][searchType] or
            #     (param in prevAvailabilitySumDict[email][searchType] and 
            #         prevAvailabilitySumDict[email][searchType].get(param) != availableSum)):
            #     # Send an email to the address comprising of all the details
            #     dataCollectDict[email] = { **dataCollectDict.get(email, {}), **sT }
            #     # This is needed for conditional check
            #     prevAvailabilitySumDict[email] = { **prevAvailabilitySumDict.get(email, {}), **sT }
            isChange = False
            if email not in prevAvailabilitySumDict:
                prevAvailabilitySumDict[email] = sT
                dataCollectDict[email] = sT
                isChange = True
            elif searchType not in prevAvailabilitySumDict[email]:
                prevAvailabilitySumDict[email] = {**prevAvailabilitySumDict[email], **sT }
                isChange = True
                dataCollectDict[email] = { **dataCollectDict[email], **sT }
            elif param not in prevAvailabilitySumDict[email][searchType] or (
                param in prevAvailabilitySumDict[email][searchType] and 
                prevAvailabilitySumDict[email][searchType][param] != availableSum
            ):
                prevAvailabilitySumDict[email][searchType] = {
                    **prevAvailabilitySumDict[email][searchType], 
                    **sT.get(searchType)
                }
                isChange = True
            
            if isChange:
                if email not in dataCollectDict:
                    dataCollectDict[email] = sT
                elif searchType not in dataCollectDict[email]:
                    dataCollectDict[email] = {**dataCollectDict[email], **sT }
                else:
                    dataCollectDict [email][searchType] = {
                        **dataCollectDict.get(email, {}).get(searchType, {}), 
                        **sT.get(searchType)
                    }
        logger.debug(prevAvailabilitySumDict)
    return dataCollectDict


def prepareEmailContent(emailSearchTypeParamsDict:Dict[str, Dict[str, Dict[int, int]]]) -> Dict[str, str]:
    contentDict = {}
    for email, searchTypeDict in emailSearchTypeParamsDict.items():
        availabilityContent = ''
        
        pincodes = []
        if searchTypeDict.get("PINCD") is not None:
            # pincodes = '\n'.join([f'<td>{p}</td><td>{av}</td>' for p, av in searchTypeDict["PINCD"].items()])
            pincodes = '\n'.join([f'<tr><td>{p}</td><td>{av}</td></tr>' for p, av in searchTypeDict["PINCD"].items()])
            availabilityContent += 'Pincodes Availability:\n' + pincodes
        pincodeTable = f'''
            <br>
            <table style="border: black 0.5px;">
                <thead>
                    <tr>
                        <th>Pincode</th>
                        <th>Availability</th>
                    </tr>
                </thead>
                <tbody>
                    {pincodes}
                </tbody>
            </table>
        ''' if len (pincodes) > 0 else ''
        
        districts = []
        if searchTypeDict.get("STDIS") is not None:
            db = next(get_db())
            disList = []
            for d,av in searchTypeDict["STDIS"].items():
                dDict = get_dis_state_nm(db, d)
                # disList.append(f"{dDict['district_name']}, {dDict['state_name']}: {av}")
                disList.append(f"<tr><td>{dDict['district_name']}</td><td>{dDict['state_name']}</td><td>{av}</td></tr>")
            districts = '\n'.join(disList)
            availabilityContent += '\n\n' if availabilityContent else '' + 'District Availability:\n' + districts
        
        disTable = f'''
            <br>
            <table style="border: black 0.5px;">
                <thead>
                    <tr>
                        <th>District</th>
                        <th>State</th>
                        <th>Availability</th>
                    </tr>
                </thead>
                <tbody>
                    {districts}
                </tbody>
            </table>
        ''' if len(districts) > 0 else ''
        
        
        contentDict[email] = f'''
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <style type="text/css" media="screen">
                               
                table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
                th, td {{ padding: 2px; }}

            </style>
        </head>
        <body>
            <p>
                Hi,<br>
                This is an automated message from CoWin Notification Service.<br>
                Currently some windows are open for vaccination scheduling.<br>
                Hurry up and book your slots.
            </p>
            {disTable + pincodeTable}
            <p><strong>Note</strong>: Please do not reply to this mailer.</p>
        </body>
        </html>
        '''
        
        # contentDict[email] = f'''
        #     Hi,
        #         This is an automated message from CoWin Notification Service
        #         Currently some windows are open for vaccination scheduling.
        #         Hurry up and book your slots.

        #     {disTable + pincodeTable}
        
        #     Note: Please do not reply to this mailer.
        # '''
    return contentDict


def sendEmailV2(emailSubDict:Dict[str, str]):
    if emailSubDict:
        logger.info(f'Send EmailV2 method started')
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = os.getenv('COWIN_EMAILER_EMAIL')
        password = os.getenv('COWIN_MAILER_PWD')
        # message = EmailMessage()
        for email, content in emailSubDict.items():    
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                message = MIMEMultipart(
                    "alternative", None, [MIMEText(content,'html')])
                
                message['To'] = email
                message['Subject'] = 'Availability of slots to book in CoWin App'
                message['From'] = sender_email
                # message.set_content(content, subtype='html')
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, email, message.as_string())
                del message['To']
                logger.info(f'Sent email to {email}')
    else:
        logger.info('Currently there are no emails to be sent due to no change in availability')