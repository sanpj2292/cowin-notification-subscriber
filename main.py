from starlette.status import HTTP_302_FOUND
from models import Subscriber
from fastapi import FastAPI, Request
from fastapi.params import Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
from constants import LOC_BASE_URL, headers
from sqlalchemy.orm import Session
import json
import db
from db import DBDistrict, DBState, bulk_district_insert, bulk_state_insert, create_subscriber, get_db, get_district, get_states_all, get_distinct_districts

app = FastAPI()
templates = Jinja2Templates(directory="templates")
states = {}

def insert_states_first_time():
    resp_states = requests.get(f'{LOC_BASE_URL}/states', headers=headers)
    print(resp_states)
    resp_states.raise_for_status()
    states = json.loads(resp_states.text)
    # This is one-time
    dbStates = []
    for state in states['states']:
        dbState = DBState(state_id=state['state_id'], state_name=state['state_name'])
        dbStates.append(dbState)

def insert_district_for_states():
    dbDistricts = []
    for i in range(1, 38):
        resp_dist = requests.get(f'{LOC_BASE_URL}/districts/{i}', headers=headers)
        resp_dist.raise_for_status()
        districts = json.loads(resp_dist.text)
        for district in districts['districts']:
            dbDistrict = DBDistrict(district_id=district['district_id'], 
                        district_name=district['district_name'],
                        state_id=i)
            dbDistricts.append(dbDistrict)
    bulk_district_insert(next(get_db()), dbDistricts)

@app.on_event('startup')
async def startup():
    global states 
    db = next(get_db())
    allStates = get_states_all(db)
    if len(allStates) > 0:
        states['states'] = allStates
    else:
        resp_states = requests.get(f'{LOC_BASE_URL}/states', headers=headers)
        print(resp_states)
        resp_states.raise_for_status()
        states = json.loads(resp_states.text)
        # This is one-time
        dbStates = []
        for state in states['states']:
            dbState = DBState(state_id=state['state_id'], state_name=state['state_name'])
            dbStates.append(dbState)
        bulk_state_insert(db, dbStates)
        insert_district_for_states()

# @app.on_event('shutdown')
# async def shutdown():
#     await database.disconnect()

@app.get('/districts', response_class=HTMLResponse)
def get_cities(request: Request, state_id: int):
    resp_dist = requests.get(f'{LOC_BASE_URL}/districts/{state_id}', headers=headers)
    resp_dist.raise_for_status()
    districts = json.loads(resp_dist.text)
    global states
    return templates.TemplateResponse('home.html', {
        'request': request,
        'districts': districts['districts'],
        'states': states['states'],
        'state_id': state_id
    })
    

@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    global states
    return templates.TemplateResponse('home.html', {
        'request': request,
        'states': states['states']
    })

@app.get('/subscription/success', response_class=HTMLResponse)
def success(request: Request):
    global states
    return templates.TemplateResponse('success.html', {
        'request': request,
        'states': states['states']
    })

@app.post('/subscribe')
def subscribe(request: Request, email: str = Form(...), state: int=Form(...), 
        district_id: int = Form(...),DB: Session = Depends(get_db)):
    respDict = {}
    try:
        subscriber = Subscriber(email=email, 
                        state_id=state, district_id=district_id,
                        active=True)
        create_subscriber(DB, subscriber=subscriber)
        respDict =  {
            'request': request,
            'isSubscriptionSuccess': True,
        }
        return RedirectResponse(url='/subscription/success',status_code=HTTP_302_FOUND)
    except Exception as inst:
        status_code = 500
        respDict =  {
            'request': request,
            'isSubscriptionSuccess': False,
            'error_message': inst
        }
        return templates.TemplateResponse('home.html', respDict, status_code=status_code)


def url_for_query(request: Request, name: str, **params: str) -> str:
    import urllib
    url = request.url_for(name)
    parsed = list(urllib.parse.urlparse(url))
    parsed[4] = urllib.parse.urlencode(params)
    return urllib.parse.urlunparse(parsed)

templates.env.globals['url_for_query'] = url_for_query