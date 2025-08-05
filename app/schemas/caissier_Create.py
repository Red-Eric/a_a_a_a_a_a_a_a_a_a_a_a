from pydantic import BaseModel  

class CaissierCreate(BaseModel):
    email : str
    mdp : str
    role : str
    access : str
    
    