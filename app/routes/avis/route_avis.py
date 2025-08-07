from fastapi import APIRouter
from app.models.avis import Avis
from app.schemas.avis_create import AvisCreate
from app.models.etablissement import Etablissement
from app.models.client import Client
from app.models.chambre import Chambre
from app.models.plat import Plat

router = APIRouter()

@router.get("")
async def getAllAvis():
    avis = await Avis.all().order_by("-id")
    return {
        "message" : "Voici les avis",
        "avis" : avis
    }



@router.get("/etablissement/{etab_id}")
async def getAvisByEtablissement(etab_id : int):
    etab = await Etablissement.get_or_none(id = etab_id)
    
    if not etab:
        return {
            "message" : "etablissement introuvable"
        }
    
    
    avis = await Avis.filter(etablissement = etab).all().order_by("-id")
    
    return {
        "message" : "Voici les avis",
        "avis" : avis
    }
    
@router.get("/plat/{id_plat}")
async def getAvisByPlat(id_plat : int):
    plat_ = await Plat.get_or_none(id = id_plat)
    
    if not plat_:
        return {
            "message" : "Plat Introuvable"
        }
    
    avis = await Avis.filter(plat = plat_).all().order_by("-id")
    
    return {
        "message" : f"Voici la liste des avis du plat {plat_.libelle}",
        "avis" : avis
    }

@router.get("/chambre/{id_chambre}")
async def getAvisByChambre(id_chambre : int):
    chambre_ = await Chambre.get_or_none(id = id_chambre)
    
    if not chambre_:
        return {
            "message" : "Chambre Introuvable"
        }
    
    avis = await Avis.filter(chambre = chambre_).all().order_by("-id")
    
    return {
        "message" : f"Voici la liste des avis du plat {chambre_.numero}",
        "avis" : avis
    }
    

    
@router.delete("/{id_}")
async def deleteAvis(id_ : int):
    avisToDel = await Avis.get_or_none(id = id_)
    if not avisToDel:
        return {
            "message" : "Avis Introuvable"
        }        
    await avisToDel.delete()
    return {
        "message" : "Avis suprrimer avec succes"
    }

@router.post("")
async def addAvis(item : AvisCreate):
    client_ = await Client.get_or_none(id = item.client_id)
    plat_ = None
    etab_ = None
    chambre_ = None
    if not client_:
        return {
            "message" : "client non trouver"
        }
        
    if item.chambre_id:
        chambre_ = await Chambre.get_or_none(id = item.chambre_id)
        if not chambre_:
            return {
                "message" : "chambre non trouver"
            }   
        
    if item.etablissement_id:
        etab_ = await Etablissement.get_or_none( id = item.etablissement_id)
        if not etab_:
            return {
                "message" : "etab non trouver"
            }
        
    if item.plat_id:
        plat_ = await Plat.get_or_none( id = item.plat_id)
        if not plat_:
            return {
                "message" : "plat non trouver"
            }
    
    avis_ = await Avis.create(
        client_id = item.client_id,
        note = item.note,
        comment = item.comment,
        
        plat = plat_,
        chambre = chambre_,
        etablissement = etab_
    )
    
    return {
        "message" : "Avis Ajouter",
        "avis" :avis_
    }
    
