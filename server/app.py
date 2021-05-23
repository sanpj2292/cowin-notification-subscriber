import uvicorn
from multiprocessing import Process
from background_task import notifyAvailabilityByEmail
import os

def runApp():
    uvicorn.run('main:app', host='0.0.0.0', port=4200)

if __name__ == '__main__':
    appProcess = Process(target=runApp)
    notifyProcess = Process(target=notifyAvailabilityByEmail)
    appProcess.start()
    notifyProcess.start()
