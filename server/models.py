from pydantic import BaseModel

    
# A Pydantic Place
class Subscriber(BaseModel):
    email : str
    district_id : int
    state_id : int
    active: bool = False
    class Config:
        orm_mode = True

class SubscriberPincodeModel(BaseModel):
    email: str
    pincode: int
    search_type: str = "PINCD"
    class Config:
        orm_mode=True

class SubscribeReqModel(BaseModel):
    email: str
    state_id: int 
    district_id: int
    class Config:
        orm_mode = True
        
class SubscriberAllModel(BaseModel):
    email : str
    district_id : int = None
    state_id : int = None
    active: bool = False
    pincode: int = None
    search_type: str = ''
    class Config:
        orm_mode = True