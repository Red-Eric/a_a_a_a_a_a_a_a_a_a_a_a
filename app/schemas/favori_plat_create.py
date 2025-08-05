from pydantic import BaseModel

class Favori_Plat_Create(BaseModel):
    client_id : int
    etablissement_id : int
    plat_id : int
    chambre_id : int