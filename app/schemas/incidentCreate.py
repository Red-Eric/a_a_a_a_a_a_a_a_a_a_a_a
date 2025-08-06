from pydantic import BaseModel

class IncidentCreate(BaseModel):

    id :str
    
    nom : str
    
    equipement_id : int
    
    title : str
    
    description : str
    
    severity : str
    
    status : str
    