from pydantic import BaseModel

class EquipementCreate(BaseModel):
    id : str
    nom : str
    type : str
    localisation : str
    status : str
    description : str
    etablissement_id : int