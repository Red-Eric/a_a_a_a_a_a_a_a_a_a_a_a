from pydantic import BaseModel

class IncidentCreate(BaseModel):


    
    equipement_id : str
    
    title : str
    
    description : str
    
    severity : str
    
    status : str
    