from pydantic import BaseModel

class Product_Create(BaseModel):
    nom : str
    quantite : int
    etablissement_id : int
    seuil_stock : int
    prix : int
    personnel_id : int
    
