from pydantic import BaseModel
from typing import Optional
from app.enum.methode_paiement import MethodePaiement
from datetime import datetime

class PaiementReservationCreate(BaseModel):
    montant_total: int
    date_de_paiement : datetime
    mode: MethodePaiement = MethodePaiement.MOBILE_MONEY
    reservation_id: int
    client_id : int
    personnel_id: Optional[int] = None
    etablissement_id : int
    
