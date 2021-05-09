import uvicorn
from multiprocessing import Process
from background_task import notifyAvailabilityByEmail

def runApp():
    uvicorn.run('main:app', port=4200, reload=False)

if __name__ == '__main__':
    appProcess = Process(target=runApp)
    # notifyProcess = Process(target=notifyAvailabilityByEmail)
    appProcess.start()
    # notifyProcess.start()
    # runApp()
  