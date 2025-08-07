from fastapi import APIRouter
from app.models.favori import Favori
from app.schemas.favori_create import FavoriCreate
from app.models.etablissement import Etablissement
from app.models.client import Client
from app.models.chambre import Chambre
from app.models.plat import Plat

router = APIRouter()

@router.get("")
async def getByEtablissement():
    favoriToADD = await Favori.all().order_by("-id")
    return {
        "message" : "Voici les Favori",
        "favoris" : favoriToADD
    }
    
@router.get("/chambre/client/{id_cli}")
async def get_chambres_favoris_by_client(id_cli: int):
    cli = await Client.get_or_none(id=id_cli)
    if not cli:
        return {"message": "Client introuvable"}

    favoris = await Favori.filter(client=cli).exclude(chambre=None).order_by("-id").prefetch_related("chambre")
    
    return {
        "message": "Voici les favoris chambre du client",
        "favoris": favoris
    }


@router.get("/plat/client/{id_cli}")
async def get_plats_favoris_by_client(id_cli: int):
    cli = await Client.get_or_none(id=id_cli)
    if not cli:
        return {"message": "Client introuvable"}

    favoris = await Favori.filter(client=cli).exclude(plat=None).order_by("-id").prefetch_related("plat")

    return {
        "message": "Voici les favoris plat du client",
        "favoris": favoris
    }


    
        
@router.delete("/{id_}")
async def deleteFavori(id_ : int):
    FavoriToDel = await Favori.get_or_none(id = id_)
    if not FavoriToDel:
        return {
            "message" : "Favori Introuvable"
        }        
    await FavoriToDel.delete()
    return {
        "message" : "Favori suprrimer avec succes"
    }

@router.post("")
async def addFavori(item : FavoriCreate):
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
    
    Favori_ = await Favori.create(
        client_id = item.client_id,
        plat = plat_,
        chambre = chambre_,
        etablissement = etab_
    )
    
    return {
        "message" : "Favori Ajouter",
        "favori" :Favori_
    }
    
