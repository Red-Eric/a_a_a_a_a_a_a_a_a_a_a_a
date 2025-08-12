from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.models.reservation import Reservation
from app.schemas.reservation_create import ReservationCreate, ReservationPatch
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
from app.models.notification import Notification
from app.websocket.notification_manager import notification_manager
from collections import defaultdict
from app.enum.etat_chambre import EtatChambre
from tortoise.contrib.pydantic import pydantic_model_creator

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

    chambre_ = await Chambre.get_or_none(id=item.chambre_id).prefetch_related("etablissement")
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

        await Notification.create(
            message=f"La réservation « {reservation.id} » a été ajoutée.",
            lu=False,
            etablissement=chambre_.etablissement
        )

        await notification_manager.send_to_etablissement(
            etablissement_id=chambre_.etablissement_id,
            event="reservation_create",
            payload={"message": f"La réservation « {reservation.id} » a été Ajouter"}
        
        )

    return {
        "message": "Réservation créée avec succès",
        "reservation_id": reservation.id
    }




@router.get("")
async def list_reservations():
    reservations = await Reservation.all().order_by("-id")
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

    chambre_ = await Chambre.get_or_none(id=item.chambre_id).prefetch_related("etablissement")
    if not chambre_:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")

    # Mise à jour manuelle des champs
    reservation.date_arrivee = item.date_arrivee
    reservation.date_depart = item.date_depart
    reservation.duree = item.duree
    reservation.statut = item.statut
    reservation.nbr_adultes = item.nbr_adultes
    reservation.nbr_enfants = item.nbr_enfants
    reservation.mode_checkin = item.mode_checkin
    reservation.code_checkin = item.code_checkin
    reservation.client_id = item.client_id
    reservation.chambre_id = item.chambre_id
    reservation.articles = [article.dict() for article in item.articles] if item.articles else []
    reservation.arhee = item.arhee.dict() if item.arhee else {}

    

    await reservation.save()

    await Notification.create(
        message=f"La réservation « {reservation.id} » a été modifiée.",
        lu=False,
        etablissement=chambre_.etablissement
    )

    await notification_manager.send_to_etablissement(
        etablissement_id=chambre_.etablissement_id,
        event="reservation_update",
        payload={"message": f"La réservation « {reservation.id} » a été modifier"}
    )

    return {
        "message": "Réservation mise à jour avec succès",
        "reservation": await reservation.values()
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



@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int):
    reservation = await Reservation.filter(id=reservation_id).prefetch_related("chambre__etablissement").first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    etablissement = None
    if reservation.chambre and reservation.chambre.etablissement:
        etablissement = reservation.chambre.etablissement

    if etablissement:
        await Notification.create(
            message=f"La réservation « {reservation_id} » a été supprimée.",
            lu=False,
            etablissement=etablissement
        )

        await notification_manager.send_to_etablissement(
            etablissement_id=etablissement.id,
            event="reservation_delete",
            payload={"message": f"La réservation « {reservation.id} » a été supprimée."}
        )

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
    

@router.get("/revenu/etablissement/{etablissement_id}")
async def revenu_par_etablissement(etablissement_id: int):
    reservations = await Reservation.filter(
        statut=Status_Reservation.CONFIRMER,
        chambre__etablissement_id=etablissement_id
    ).prefetch_related('chambre')

    revenu_par_jour = defaultdict(float)
    for res in reservations:
        if res.chambre:
            date_only = res.date_arrivee.date()
            revenu = float(res.chambre.tarif)
            revenu_par_jour[date_only] += revenu

    result = [
        {"date": date.isoformat(), "revenu_total": revenu}
        for date, revenu in sorted(revenu_par_jour.items())
    ]

    return {
        "message" : "voici les revenu journaliere de cette etablissement",
        "revenus" : result
    }
    



Reservation_Pydantic = pydantic_model_creator(Reservation)

@router.patch("/{reservation_id}")
async def update_reservation_patch(
    reservation_id: int,
    item: ReservationPatch
):
    reservation = await Reservation.get_or_none(id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    client_ = await Client.get_or_none(id=item.client_id)
    if not client_:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    chambre_ = await Chambre.get_or_none(id=item.chambre_id).prefetch_related("etablissement")
    if not chambre_:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")

    pers = await Personnel.get_or_none(id=item.personnel_id)
    if not pers:
        raise HTTPException(status_code=404, detail="Personnel non trouvé")

    statut_initial = reservation.statut

    # Mise à jour du statut uniquement
    reservation.statut = item.statut
    await reservation.save()

    if reservation.statut == Status_Reservation.CONFIRMER:
        chambre_.etat = EtatChambre.OCCUPEE
        await chambre_.save()

    if item.articles:
        if statut_initial == Status_Reservation.CONFIRMER and item.statut != Status_Reservation.CONFIRMER:
            # Retour stock (annulation)
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
                        raison=f"Annulation de la commande du client {client_.first_name or ''} {client_.last_name or ''} {client_.phone or ''}"
                    )

        elif item.statut == Status_Reservation.CONFIRMER:
            # Sortie stock (confirmation)
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
                        raison=f"Commande du client {client_.first_name or ''} {client_.last_name or ''} {client_.phone or ''}"
                    )

    etablissement_instance = await chambre_.etablissement

    await Notification.create(
        message=f"Le statut de la réservation « {reservation.id} » a été modifié à « {item.statut.value} ».",
        lu=False,
        etablissement=etablissement_instance
    )

    await notification_manager.send_to_etablissement(
        etablissement_id=chambre_.etablissement_id,
        event="reservation_patch",
        payload={"message": f"La réservation « {reservation.id} » a été patchée"}
    )

    # Utilisation du modèle Pydantic pour sérialiser la réservation
    reservation_pydantic = await Reservation_Pydantic.from_tortoise_orm(reservation)

    return {
        "message": "Statut de la réservation mis à jour avec succès",
        "reservation": reservation_pydantic
    }