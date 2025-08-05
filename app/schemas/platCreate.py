from pydantic import BaseModel, HttpUrl, Field
from typing import List

class PlatCreate(BaseModel):
    libelle: str
    type: str = "Petit dej"
    image_url: HttpUrl = Field(
        default="https://img.freepik.com/psd-gratuit/plateau-poulet-roti-delicieux-festin_632498-25445.jpg?semt=ais_hybrid&w=740"
    )
    description: str = "Plat moyenne btw"
    note: int
    prix: int
    disponible: bool = True
    ingredients: List[str]
    tags: List[str] = []
    calories: int = 500
    prep_minute: int = 15
    etablissement_id: int
