from fastapi import APIRouter
from app.models.intervention import Intervention
from app.schemas.interventionCreate import InterventionCreate
from app.models.personnel import Personnel
from app.models.equipement import Equipement
from app.models.etablissement import Etablissement

router = APIRouter()

@router.get("")
async def getAllForTest():
    return {
        "message" : "Voici la liste de tout les intervention",
        "interventions" : await Intervention.all()
    }

@router.post("")
async def addIncident(item : InterventionCreate):
    personnel = await Personnel.get_or_none(id = item.personnel_id)
    equip = await Equipement.get_or_none(id = item.equipement_id)
    
    if not personnel:
        return {
            "message" : "Personnel introuvable"
        }
    if not equip:
        return {
            "message" : "Equipement introuvable"
        }
    
    interToAdd = await Intervention.create(
        personnel = personnel,
        equipement = equip,
        description = item.description,
        status = item.status
    )
    
    return {
        "message" : "Intervention Ajouter avec succes",
        "intervention" : interToAdd
    }
    
@router.get("/etablissement/{id_etab}")
async def get_interventions_by_etablissement(id_etab: int):
    # Vérifie si l’établissement existe
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        return {"message": "Etablissement inexistant"}

    # Récupère les interventions via les équipements liés à cet établissement
    interventions = await Intervention.filter(
        equipement__etablissement_id=id_etab
    ).prefetch_related("equipement", "personnel").order_by("-date")

    # Retourne les données
    return {
        "message": "Liste des interventions pour l'établissement",
        "interventions" : interventions
        }
    
@router.get("/personnel/{id_pers}")
async def getByPersonnel(id_pers : int):
    pers = await Personnel.get_or_none(id = id_pers)
    
    if not pers:
        return {
            "message" : "personnel introuvable"
        }
    
    intervs = await Intervention.filter(personnel = pers).all()
    
    return {
        "message" : f"Voici la liste des iintervention du personnel {pers.nom}",
        
        "interventions" : intervs
    }

@router.delete("/{id_interv}")
async def deleteIntervention(id_interv : int):
    intervToDel = await Intervention.get_or_none(id = id_interv)
    if not intervToDel:
        return {
            "message" : "Intervention introuvable "
        }
        
    await intervToDel.delete()
    
    return {
        "message" : "Intervention effacer avec succes"
    }
    
