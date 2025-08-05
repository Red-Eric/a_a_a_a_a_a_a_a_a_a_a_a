from pydantic import BaseModel

class FactureCreate(BaseModel):
    montant_total : int
    paiement_id : int 
    client_id : int
    etablissement_id : int 
    description : str