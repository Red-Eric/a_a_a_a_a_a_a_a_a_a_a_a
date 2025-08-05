from pydantic import BaseModel
from typing import Optional

class Commande_plat_create(BaseModel):
    montant : int
    client_id : int
    plat_id : int
    quantite : int
    description : Optional[str] = None