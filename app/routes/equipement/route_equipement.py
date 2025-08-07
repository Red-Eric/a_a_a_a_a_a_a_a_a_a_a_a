from fastapi import APIRouter
from app.models.equipement import Equipement
from app.schemas.equipementCreate import EquipementCreate
from app.models.etablissement import Etablissement

router = APIRouter()

@router.get("")
async def getAllEquipement():
    return {
        "message" : "voici la liste de tout les equipements",
        "equipements" : await Equipement.all().order_by("-id")
    }
    
@router.get("/etablissement/{id_etab}")
async def getAllEquipement(id_etab : int):
    etab = await Etablissement.get_or_none(id = id_etab)
    if not etab:
        return {
            "message" : "introuvable etablissement"
        }
    
    eq = await Equipement.filter(etablissement = etab).all().order_by("-id")
    
    return {
        "message" : "voici la liste de tout les equipements",
        "equipements" : eq
    }
    



    
@router.post("")
async def addEquip(item : EquipementCreate):
    etab = await Etablissement.get_or_none(id = item.etablissement_id)
    if not etab:
        return {
            "message" : "Etablissement introuvable"
        }
    
    equipToAdd = await Equipement.create(
        id = item.id,
        nom = item.nom,
        type = item.type,
        localisation = item.localisation,
        status = item.status,
        description = item.description,
        etablissement = etab
    )
    
    return {
        "message" : "Equipement ajouter avec succes",
        "equipement" : equipToAdd
    }


@router.put("/{id_equipement}")
async def editEquip(item : EquipementCreate, id_equipement : str):
    editEqui = await Equipement.get_or_none(id = id_equipement)
    if not editEqui:
        return {
            "message" : "Equipement Introuvable"
        }
    
    editEqui.nom = item.nom
    editEqui.type = item.type
    editEqui.localisation = item.localisation
    editEqui.status = item.status
    editEqui.description = item.description
    
    await editEqui.save()
    
    return {
        "message" : "Equipement modifier"
    }

@router.delete("/{e_id}")
async def deleteEquip(e_id : str):
    equipToDel = await Equipement.get_or_none(id = e_id)
    
    if not equipToDel:
        return {
            "message" : "Equipement introuvable"
        }
    
    await equipToDel.delete()
    
    return {
        "message" : "Equipement effacer"
    }


