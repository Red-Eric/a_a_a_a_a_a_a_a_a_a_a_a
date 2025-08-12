from pydantic import BaseModel
from typing import Optional
from app.enum.commande_statu import CommandeStatu

class Commande_plat_create(BaseModel):
    montant : int
    client_id : int
    plat_id : int
    status : CommandeStatu = CommandeStatu.ENCOURS
    quantite : int
    description : Optional[str] = None