from typing import Dict, Optional
from pydantic import BaseModel

'''
{
    'endpoint': 'https://fcm.googleapis.com/fcm/send/e1xA97UpRkg:APA91bHZnNGgGRpTNqAAQbFsmLH3I6UrxSVLkDV1nfTh0h5s9CbxcPyhf4JO4r_3yqu_xf-RzfMKlyzuc4j17jgMXIz73L3Ous89sYq6h30Fh52ckkLaK96nonp2KUdqHsAq0Pk1dO8s',
    'expirationTime': None, 
    'keys': {
        'p256dh': 'BAqcMvv3ygoWzlYObEjsUEQ8Gp4p5MvhUDJ33NJbvqcr-5yhVXNtF_3XB7tH-6r2lCwopSqP8UdMXbwlHKOpRnU', 
        'auth': 'w5zvDfu-x6UL-VO0yTFhKQ'
    }
}
    
    
{
    'endpoint': 'https://fcm.googleapis.com/fcm/send/e1xA97UpRkg:APA91bHZnNGgGRpTNqAAQbFsmLH3I6UrxSVLkDV1nfTh0h5s9CbxcPyhf4JO4r_3yqu_xf-RzfMKlyzuc4j17jgMXIz73L3Ous89sYq6h30Fh52ckkLaK96nonp2KUdqHsAq0Pk1dO8s', 
    'expirationTime': None, 
    'keys': {
        'p256dh': 'BAqcMvv3ygoWzlYObEjsUEQ8Gp4p5MvhUDJ33NJbvqcr-5yhVXNtF_3XB7tH-6r2lCwopSqP8UdMXbwlHKOpRnU', 
        'auth': 'w5zvDfu-x6UL-VO0yTFhKQ'
    }
}

{
    'endpoint': 'https://wns2-sg2p.notify.windows.com/w/?token=BQYAAADVEnMEpUlhYnjQKSIVAO4xKKxY6D75ufVxQGBBJxpRUWfbhyXiU6ABXaLZt7%2bZyuR93Z4cPKw9TxyPE%2bpeuU3GfwTeYQ4qquAodKVT1xdFxUCDxv4o8JHibsdaRXYeEHobQKX%2f5MrhgGr%2bqlQ6DJQ1%2fQ%2fGfKF0mFnPMf6ff29B1a031M4PsEmbtLCaYFybdh%2bCzzet35GyRfqoGuzlu3R%2fBMS9ofkUPZlEZMjp4aq6ptNeX%2bjKrVcc0VZiqgGss7KzZGCmrcbH4BdNYJc5jyLNh4NiVRRoPR9Ob3loXzY4S%2fKjZYsQb4L9ZzmDQ%2bEw1Xo%3d', 
    'expirationTime': None, 
    'keys': {
        'p256dh': 'BNXEBjeYRMNOMZGo9nt5-YWyLNfOlqk6Lobc9Tvanz-HmmnEM9gh5KMN0PGvkgIimhe0b1p59W9x4oEumrXP9Jg', 
        'auth': 'KqYAalm9fRtwX2mPumvSZw'
    }
}
'''

class PushNotificationKeysModel(BaseModel):
    p256dh:str = ''
    auth:str = ''
class PushNotificationModel(BaseModel):
    
    endpoint:str = ''
    expirationTime:Optional[float] = 0
    keys:PushNotificationKeysModel
    
    class Config:
        orm_mode = True
# A Pydantic Place
class Subscriber(BaseModel):
    email : str
    district_id : int
    state_id : int
    active: bool = False
    min_age:int = 0
    class Config:
        orm_mode = True

class SubscriberPincodeModel(BaseModel):
    email: str
    pincode: int
    search_type: str = "PINCD"
    min_age:int = 0
    pushNotification = {}
    class Config:
        orm_mode=True

class SubscribeReqModel(BaseModel):
    email: str
    state_id: int 
    district_id: int
    min_age:int = 0
    pushNotification = {}
    class Config:
        orm_mode = True
        
class SubscriberAllModel(BaseModel):
    email : str
    district_id : int = None
    state_id : int = None
    active: bool = False
    pincode: int = None
    search_type: str = ''
    min_age: int = 0
    pushNotification = {}
    class Config:
        orm_mode = True