from pydantic import BaseModel
from typing import Optional

class AvisCreate(BaseModel):
    comment : str
    note : int
    client_id : int
    #--------------------------------------------------
    chambre_id : Optional[int] = None
    etablissement_id : Optional[int] = None
    plat_id : Optional[int] = None
        