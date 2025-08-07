from pydantic import BaseModel

class InterventionCreate(BaseModel):
    personnel_id : int
    equipement_id : int
    description : str
    status : str