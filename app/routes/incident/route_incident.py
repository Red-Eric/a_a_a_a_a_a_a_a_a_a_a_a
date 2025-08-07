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

async def generate_incident_id():
    last_incident = await Incident.filter(id__startswith="INC-").order_by("-id").first()
    if last_incident:
        last_number = int(last_incident.id.replace("INC-", ""))
        new_number = last_number + 1
    else:
        new_number = 1
    return f"INC-{new_number:04d}"

@router.post("")
async def addIncident(item : IncidentCreate):
    equip = await Equipement.get_or_none(id = item.equipement_id)
    if not equip:
        return {
        "message" : "equipement introuvable"
        }
        
    generated_id = await generate_incident_id()
    
    inc = await Incident.create(
       id = generated_id ,       
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