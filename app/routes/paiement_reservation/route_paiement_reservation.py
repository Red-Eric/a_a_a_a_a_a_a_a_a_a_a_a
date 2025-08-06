from fastapi import APIRouter
from app.models.paiement_reservation import Paiement_reservation
from app.models.client import Client
from app.models.etablissement import Etablissement
from app.models.reservation import Reservation
from tortoise.functions import Sum
from app.schemas.paiement_reservation_create import PaiementReservationCreate
from app.models.personnel import Personnel

router = APIRouter()

@router.get("")
async def getAllPaiement():
    allPaiement = await Paiement_reservation.all().order_by("-id")
    return {
        "message" : "Voici le nombre de paiement",
        "paiements" : allPaiement
    }
    
@router.get("/fond/etablissement/{id_}")
async def getMoneyEtab(id_: int):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return {"message": "Etablissement introuvable"}
    
    total = await Paiement_reservation.filter(etablissement_id=id_).aggregate(total_argent=Sum("montant_total"))

    return {
        "etablissement_id": id_,
        "total_argent": total["total_argent"] or 0
    }
    

@router.post("")
async def addPaiement(item : PaiementReservationCreate):
    caissierRef = await Personnel.get_or_none(id=item.personnel_id)
    if not caissierRef:
        return {"message": "Caissier introuvable"}
    etab = await Etablissement.get_or_none(id=item.etablissement_id)
    if not etab:
        return {"message": "Établissement introuvable"}
    cli = await Client.get_or_none(id=item.client_id)
    if not cli:
        return {"message": "Client introuvable"}
    reservation_ = await Reservation.get_or_none(id=item.reservation_id)
    if not reservation_:
        return {"message": "Réservation introuvable"}

    
    
    paiementToAdd = await Paiement_reservation.create(
        montant_total = item.montant_total,
        date_de_paiement = item.date_de_paiement,
        mode = item.mode,
        reservation_id = item.reservation_id,
        etablissement_id = item.etablissement_id,
        personnel_id = item.personnel_id,
        client_id = item.client_id
    )
    
    return {
        "message" : "Paiement Effectuer",
        "paiement" : paiementToAdd
    }
