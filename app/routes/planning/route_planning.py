from fastapi import APIRouter
from app.models.planningEvent import PlanningEvent
from app.enum.planing_event_status import PlanningEventStatus
from app.enum.planning_event_type import PlanningEventType
from app.models.etablissement import Etablissement
from app.schemas.planning_create import Planning_create
from app.models.personnel import Personnel

router =  APIRouter()

@router.get("")
async def getAllPlanning():
    allPlanning = await PlanningEvent.all().order_by("-id")
    
    return {
        "message" : "Voici liste de tout les Planning",
        "plannings" : allPlanning
    }
    
@router.get("/{id_etab}")
async def getPlanningByID(id_etab):
    etab_ = await Etablissement.get_or_none(id= id_etab)
    if not etab_:
        return {
            "message" : "Introuvable Etab"
        }
    
    plannings = await PlanningEvent.filter(etablissement =  etab_).all().order_by("-id")
    
    return {
        "message" : f"voici les planning de l etablissement {etab_.nom}",
        "plannings" : plannings
    }


@router.post("")
async def addPlanning(item : Planning_create):
    
    etab_ = await Etablissement.get_or_none(id = item.etablissement_id)
    personnel_ = await Etablissement.get_or_none(id = item.personnel_id)
    res_ = await Etablissement.get_or_none(id = item.responsable_id)
    
    if not personnel_:
        return {
            "message" : "Personnel Introuvable"
        }
    if not res_:
        return {
            "message" : "Personnel Introuvable"
        }

    if not etab_:
        return {
            "message" : "Etablissemnt introuvabel"
        }
    
    planningToAdd = await PlanningEvent.create(
        type = item.type,
        status = item.status,
        titre = item.titre,
        description = item.description,
        dateDebut = item.dateDebut,
        dateFin = item.dateFin,
        etablissement = etab_,
        personnel = personnel_,
        responsable = res_
    )
    
    return {
        "message" : "planning Ajouter avec succes",
        "planning" : planningToAdd
    }

@router.delete("/{id_}")
async def deletePlanning(id_ : int):
    planningToDel = await PlanningEvent.get_or_none(id = id_)
    if not planningToDel:
        return {
            "message" : "Planning introuvable"
        }
    
    await planningToDel.delete()
    
    return {
        "message" : "planning effacer avec succes"
    }