from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.enum.status_reservation import Status_Reservation
from app.enum.checking_type import CheckingType
from app.enum.methode_paiement import MethodePaiement

class Article(BaseModel):
    nom: str
    quantite: int
    prix: int

class Arhee(BaseModel):
    montant: int
    date_paiement : datetime
    mode_paiement : MethodePaiement
    commentaire : str

class ReservationCreate(BaseModel):
    date_arrivee: datetime
    date_depart: datetime
    duree: int
    statut: Status_Reservation = Status_Reservation.EN_ATTENTE
    nbr_adultes: int
    nbr_enfants: int
    client_id: int
    chambre_id: int
    mode_checkin: CheckingType = CheckingType.MANUEL
    code_checkin: Optional[str] = None
    articles: Optional[List[Article]] = None
    arhee: Optional[Arhee] = None
