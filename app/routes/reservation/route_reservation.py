from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.models.reservation import Reservation
from app.schemas.reservation_create import ReservationCreate
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.models.client import Client
from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from tortoise.transactions import in_transaction
from app.models.mouvement_stock import MouvementStock
from app.models.product import Produit
from app.models.personnel import Personnel
from app.enum.type_mouvement_stock import Type_mouvement_stock
from app.enum.status_reservation import Status_Reservation

router = APIRouter()

class ReservationRead(ReservationCreate):
    id: int

    class Config:
        orm_mode = True




@router.post("")
async def create_reservation(item: ReservationCreate):
    client_ = await Client.get_or_none(id=item.client_id)
    if not client_:
        return {"message": "Client 404"}

    chambre_ = await Chambre.get_or_none(id=item.chambre_id)
    if not chambre_:
        return {"message": "Chambre 404"}

    async with in_transaction():
        reservation = await Reservation.create(
            date_arrivee=item.date_arrivee,
            date_depart=item.date_depart,
            duree=item.duree,
            statut=item.statut,
            nbr_adultes=item.nbr_adultes,
            nbr_enfants=item.nbr_enfants,
            mode_checkin=item.mode_checkin,
            code_checkin=item.code_checkin,
            client_id=item.client_id,
            chambre_id=item.chambre_id,
            articles=[article.dict() for article in item.articles] if item.articles else [],
            arhee=item.arhee.dict() if item.arhee else {}
        )

    return {
        "message": "Réservation créée avec succès",
        "reservation_id": reservation.id
    }



@router.get("")
async def list_reservations():
    reservations = await Reservation.all()
    return {
        "message" : "voici la liste des reser",
        "reservations" : reservations
    }


@router.get("/{reservation_id}")
async def get_reservation(reservation_id: int):
    reservation = await Reservation.get_or_none(id=reservation_id)
    if not reservation:
        return {
            "message" : "Reservation Introuvable"
        }
    return {
        "message" : "voici la reservation",
        "reservations" : reservation
    }


@router.put("/{reservation_id}")
async def update_reservation(reservation_id: int, item: ReservationCreate):
    reservation = await Reservation.get_or_none(id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    client_ = await Client.get_or_none(id=item.client_id)
    if not client_:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    chambre_ = await Chambre.get_or_none(id=item.chambre_id)
    if not chambre_:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")



    update_data = item.dict()
    update_data["articles"] = [article.dict() for article in item.articles]
    update_data["arhee"] = item.arhee.dict()

    await reservation.update_from_dict(update_data)
    
    await reservation.save()
    
    

    return {
        "message" : "Voici la reservation",
        "reservation" : reservation
    }

@router.get("/status/{status_reservation}/{etab_id}")
async def get_stats_by_status_and_etab(status_reservation: Status_Reservation, etab_id: int):
    etab = await Etablissement.get_or_none(id=etab_id)
    if not etab:
        return {
            "message" : "Etablissement introuvable"
        }

    chambres = await Chambre.filter(etablissement_id=etab_id).all()
    chambre_map = {chambre.id: chambre for chambre in chambres}

    chambre_ids = list(chambre_map.keys())

    reservations = await Reservation.filter(
        statut=status_reservation,
        chambre_id__in=chambre_ids
    )

    prix_total = 0.0
    for res in reservations:
        chambre = chambre_map.get(res.chambre_id)
        if chambre and chambre.tarif:
            prix_total += float(chambre.tarif) * res.duree

    return {
        "message": f"{len(reservations)} réservation(s) avec statut '{status_reservation.value}' dans l’établissement {etab.nom}",
        "prix_total": prix_total,
        "nombres": len(reservations)
    }

@router.patch("/{reservation_id}")
async def update_reservation_patch(reservation_id: int, item : ReservationCreate, id_personnel : int = Body(...)):
    reservation = await Reservation.get_or_none(id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    client_ = await Client.get_or_none(id=item.client_id)
    if not client_:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    chambre_ = await Chambre.get_or_none(id=item.chambre_id)
    if not chambre_:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")


    pers = await Personnel.get_or_none(id=id_personnel)
    if not pers:
        raise HTTPException(status_code=404, detail="personnel non trouvé")


    statut_initial = reservation.statut

    reservation.statut = item.statut
    await reservation.save()

    if statut_initial == Status_Reservation.CONFIRMER and item.statut != Status_Reservation.CONFIRMER:
        for article in item.articles:
            prod_ = await Produit.get_or_none(nom=article.nom)

            
            
            if prod_:
                prod_.quantite += article.quantite
                await prod_.save()

                await MouvementStock.create(
                    produit=prod_,
                    personnel=pers,
                    quantite=article.quantite,
                    type=Type_mouvement_stock.ENTRE,
                    raison=f"Annulation de la commande du client {client_.first_name} {client_.last_name} {client_.phone}"
                )

            
    elif item.statut == Status_Reservation.CONFIRMER:
        for article in item.articles:
            prod_ = await Produit.get_or_none(nom=article.nom)

            if prod_:

                if prod_.quantite < article.quantite:
                    raise HTTPException(status_code=400, detail=f"Stock insuffisant pour le produit {article.nom}")

                prod_.quantite -= article.quantite
                await prod_.save()

                await MouvementStock.create(
                    produit=prod_,
                    personnel=pers,
                    quantite=article.quantite,
                    type=Type_mouvement_stock.SORTIE,
                    raison=f"Commande du client {client_.first_name} {client_.last_name} {client_.phone}"
                )

    return {
        "message" : "Voici la reservation",
        "reservation" : reservation
    }


@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int):
    reservation = await Reservation.get_or_none(id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    await reservation.delete()
    return {"message": "Réservation supprimée avec succès"}

# ------------------------ Super Admin

@router.get("/recent/all/{days_}", response_model=List[ReservationRead])
async def get_recent_reservations(days_: int):
    cutoff_date = datetime.utcnow() - timedelta(days=days_)
    reservations = await Reservation.filter(date_creation__gte=cutoff_date).all()
    return {
        "message" : f"voici la liste des reservation de ces {cutoff_date}",
        "reservations" : reservations
    }

#-------------------- Etablissement

@router.get("/recent/{id_etab}/{days_}", response_model=List[ReservationRead])
async def get_recent_reservations_by_etab(id_etab: int, days_: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement introuvable")
    
    chambres_ = await Chambre.filter(etablissement = etab).all()
    reservations = []

    cutoff_date = datetime.utcnow() - timedelta(days=days_)
    
    for x in chambres_:
        xRes = await Reservation.filter(date_creation__gte=cutoff_date, etablissement_id=etab.id).all()
        reservations.extend(xRes)
        
    return {
        "message" : f"voici la liste des reservation de ces {cutoff_date} jours , de l' etablissement {etab.nom}",
        "reservation" : reservations
    }


@router.get("/etablissement/{id_etab}")
async def get_reservations_by_etablissement(id_etab: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement introuvable")
    
    chambre_ = await Chambre.filter(etablissement = etab).all()
    
    reservations = []
    
    for x in chambre_:
        xRes = await Reservation.filter(chambre=x).all()
        reservations.extend(xRes)
    
    return {
        "message" : f"voici la liste des reservation de l etablissement {etab.nom}",
        "reservations" : reservations
    }
    

#----------------------------------- Cliii

@router.get("/client/{id_client}")
async def get_reservations_by_client(id_client: int):
    client = await Client.get_or_none(id=id_client)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    reservations = await Reservation.filter(client_id=client.id).all()
    return {
        "message" : f"voici la liste du reservation du client {client.first_name} {client.last_name}",
        "reservations" : reservations
    }
    
