from pydantic import BaseModel
from app.enum.planing_event_status import PlanningEventStatus
from app.enum.planning_event_type import PlanningEventType
from datetime import datetime

class Planning_create(BaseModel):
    type : PlanningEventType = PlanningEventType.REUNION
    status : PlanningEventStatus = PlanningEventStatus.EN_ATTENTE
    titre : str
    description : str
    
    dateDebut : datetime
    dateFin : datetime
    
    etablissement_id : int
    
    personnel_id : int
    
    responsable_id : int
