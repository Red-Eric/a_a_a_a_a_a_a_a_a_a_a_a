from pydantic import BaseModel
from app.enum.conge_type import CongerTypee
from app.enum.conge_status import CongerStatus
from datetime import datetime

class Conger_Create(BaseModel):
    type : CongerTypee = CongerTypee.MALADIE
    status : CongerStatus = CongerStatus.EN_ATTENTE
    dateDebut : datetime
    dateDmd : datetime
    
    dateFin : datetime
    raison : str
    
    fichierJoin : str
    
    etablissement_id : int
    
    personnel_id : int
    