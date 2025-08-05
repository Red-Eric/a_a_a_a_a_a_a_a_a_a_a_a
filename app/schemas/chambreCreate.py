from pydantic import BaseModel
from app.enum.room_type import TypeChambre
from decimal import Decimal
from typing import List, Optional

class ChambreCreate(BaseModel):
    id_etablissement: int
    numero: str
    capacite: int
    equipements: List[str]
    categorie: TypeChambre
    tarif: Decimal
    description: Optional[str] = "Une chambre idéale pour une famille de 4 personnes"
    photo_url: Optional[str] = "https://www.domainedarondeau.com/wp-content/uploads/2017/06/Hotel-7-large-2.jpg"
