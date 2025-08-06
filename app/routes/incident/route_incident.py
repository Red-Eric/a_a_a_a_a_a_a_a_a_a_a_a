from fastapi import APIRouter
from app.models.incident import Incident
from app.schemas.incidentCreate import IncidentCreate
from app.models.equipement import Equipement

router = APIRouter()

@router.get("")
async def getAllInc():
    return {
        "message" : "Voici les incident",
        "incindents" : await Incident.all().order_by("-id")
    }

@router.post("")
async def addIncident(item : IncidentCreate):
    equip = await Equipement.get_or_none(id = item.equipement_id)
    if not equip:
        return {
        "message" : "equipement introuvable"
        }
    
    inc = await Incident.create(
       id = item.id,
    
        nom = item.nom,
        
        equipement = equip,
        
        title = item.title,
        
        description = item.description,
        
        severity = item.severity,
        
        status = item.status 
    )
    
    return {
        "message" : "Incident added",
        "return" : inc
    }

@router.delete("/{id_}")
async def deleteIncident(id_ : int):
    inc = await Incident.get_or_none(id = id_)
    if not inc:
        return {
            "message" : "Introuvable inc"
        }
    
    await inc.delete()
    
    return {
        "message" : "Incident effacer avec succes"
    }