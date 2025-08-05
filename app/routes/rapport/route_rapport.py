from fastapi import APIRouter, HTTPException
from app.models.rapport import Rapport
from app.models.etablissement import Etablissement
from app.models.personnel import Personnel
from app.schemas.rapport_create import Rapport_Create
from app.enum.status_rapport import Status_rapport
from datetime import timedelta, datetime

router = APIRouter()

@router.get("")
async def getAllRapport():
    allRapport = await Rapport.all().select_related("personnel")
    return {
        "message": "Voici la liste de tous les rapports",
        "rapports": allRapport
    }

@router.get("/etablissement/{id_}")
async def getRapportByEtab(id_: int):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return {"message": "Établissement introuvable"}
    
    rapports = await Rapport.filter(personnel__etablissement=etab).select_related("personnel")
    return {
        "message": f"Voici la liste des rapports de l'établissement {etab.nom}",
        "rapports": rapports
    }

@router.get("/personnel/{id_}")
async def getRapportByPersonnel(id_: int):
    pers = await Personnel.get_or_none(id=id_)
    if not pers:
        return {"message": "Personnel introuvable"}
    
    rapports = await Rapport.filter(personnel=pers).select_related("personnel")
    return {
        "message": f"Voici la liste des rapports du personnel {pers.nom} {pers.prenom}",
        "rapports": rapports
    }

@router.post("")
async def addRapport(item: Rapport_Create):
    etabl_ = await Etablissement.get_or_none(id=item.etablissement_id)
    personnel = await Personnel.get_or_none(id=item.personnel_id)

    if not etabl_:
        return {"message": "Établissement introuvable"}
    if not personnel:
        return {"message": "Personnel invalide"}
    
    rapportToAdd = await Rapport.create(
        personnel=personnel,
        type=item.type,
        titre=item.titre,
        description=item.description,
        statut=Status_rapport.EN_ATTENTE
    )

    return {
        "message": f"Rapport envoyé par {personnel.nom} {personnel.prenom}",
        "rapport": rapportToAdd
    }

@router.put("/status/{status_}/{id_}")
async def changeStatus(status_: str, id_: int):
    rapport_ = await Rapport.get_or_none(id=id_)
    if not rapport_:
        return {"message": "Rapport inexistant"}
    
    rapport_.statut = status_
    await rapport_.save()
    return {
        "message": f"Statut mis à jour : {rapport_.statut}",
        "rapport": rapport_
    }

@router.delete("/{id_}")
async def deleteRapport(id_: int):
    rapportToDel = await Rapport.get_or_none(id=id_)
    if not rapportToDel:
        return {"message": "Rapport introuvable"}
    
    await rapportToDel.delete()
    return {"message": "Rapport supprimé"}

@router.get("/etablissement/recent/{etab_id}/{days_}")
async def get_recent_rapports_by_etablissement(etab_id: int, days_: int):
    limit_date = datetime.utcnow() - timedelta(days=days_)
    etab_ = await Etablissement.get_or_none(id=etab_id)
    if not etab_:
        return {"message": "Établissement introuvable"}
    
    rapports = await Rapport.filter(
        date__gte=limit_date,
        personnel__etablissement=etab_
    ).select_related("personnel")
    count_ = await rapports.count()

    return {
        "message": f"Rapports enregistrés dans les {days_} derniers jours",
        "rapports": rapports,
        "nombre": count_
    }

@router.get("/status/{status_}/{etab_id}")
async def getByStatus(status_: str, etab_id: int):
    etab_ = await Etablissement.get_or_none(id=etab_id)
    if not etab_:
        return {"message": "Établissement non trouvé"}
    
    rapports = await Rapport.filter(
        statut=status_,
        personnel__etablissement=etab_
    ).select_related("personnel")
    nbr_ = await rapports.count()
    
    return {
        "message": f"Voici la liste des rapports de statut {status_} pour l'établissement {etab_.nom}",
        "rapports": rapports,
        "nombres": nbr_
    }
