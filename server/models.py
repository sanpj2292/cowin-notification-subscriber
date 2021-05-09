from pydantic import BaseModel

    
# A Pydantic Place
class Subscriber(BaseModel):
    email : str
    district_id : int
    state_id : int
    active: bool

    class Config:
        orm_mode = True