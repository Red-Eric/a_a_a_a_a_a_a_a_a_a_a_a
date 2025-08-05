from pydantic import BaseModel
from datetime import datetime
from app.enum.status_rapport import Status_rapport
from app.enum.type_rapport import TypeRapport

class Rapport_Create(BaseModel):
    personnel_id : int
    etablissement_id : int
    type : TypeRapport = TypeRapport.MAINTENANCE
    titre : str
    description : str
    # statut : Status_rapport = Status_rapport.EN_ATTENTE