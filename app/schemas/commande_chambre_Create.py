from pydantic import BaseModel
from datetime import datetime
from datetime import date

class CommandeChambreCreate(BaseModel):
    client_id : int
    chambre_id : int
    date_debut : date
    date_fin : date
