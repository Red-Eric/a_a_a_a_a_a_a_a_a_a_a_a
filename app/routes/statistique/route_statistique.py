from fastapi import APIRouter
from app.enum.type_etablissement import Type_etablissement
from app.models.etablissement import Etablissement
from app.models.client import Client
from app.enum.account_status import AccountStatus


router = APIRouter()

#-------------------------SuperAdmin----------------

@router.get("/typeEtab")
async def getStatTypeEtab():
    nbrHotel = await Etablissement.filter(type_ = Type_etablissement.HOTELERIE).all().count()
    nbrRest = await Etablissement.filter(type_ = Type_etablissement.RESTAURATION).all().count()
    nbrHotelAndRest = await Etablissement.filter(type_ = Type_etablissement.HOTELERIE_RESTAURATION).all().count()
    
    return {
        "message" : "Voici la stat des 3",
        "nombre_hotelerie": nbrHotel,
        "nombre_restauration" : nbrRest,
        "nombre_Hotel_et_restauration" : nbrHotelAndRest
    }

@router.get("/nbrClient")
async def getNbrAllClient():
    return {
        "message" : "voici le nombre de clients total tout etablissement",
        "nombre_client" : await Client.all().count()
    }    

@router.get("/nbrEtablissement")
async def getNbrAllEtab():
    return {
        "message" : "voici le nombre d etablissement total",
        "nombre_etablissement" : await Etablissement.all().count()
    }
    
@router.get("/statut_account")
async def getNbrAllStatus():
    return{
        "message": "voici la sta blabla",
        "nombre_active" : await Client.filter(account_status = AccountStatus.ACTIVE).all().count(),
        "nombre_inactive" : await Client.filter(account_status =  AccountStatus.INACTIVE).all().count(),
        "nombre_suspendu" : await Client.filter(account_status = AccountStatus.SUSPENDED).all().count(),
        "nombre_total" : await Client.all().count()
    }

#----------------------Directeur----------------------