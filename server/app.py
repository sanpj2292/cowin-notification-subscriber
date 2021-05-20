import uvicorn
from multiprocessing import Process
from background_task import notifyAvailabilityByEmail
import os

def runApp():
    uvicorn.run('main:app', port=int(os.getnev('PORT')) or 4200, reload=True, reload_dirs=['templates'])

if __name__ == '__main__':
    appProcess = Process(target=runApp)
    notifyProcess = Process(target=notifyAvailabilityByEmail)
    appProcess.start()
    notifyProcess.start()
  