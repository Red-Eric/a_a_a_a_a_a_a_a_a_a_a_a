from fastapi import APIRouter, HTTPException
from app.models.client import Client
from app.models.etablissement import Etablissement
from app.schemas.clientCreate import Client_Create
from app.enum.account_status import AccountStatus
from datetime import datetime, timedelta
from itertools import count
from tortoise.functions import Count
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("")
async def add_user(client: Client_Create):
    existing = await Client.get_or_none(email=client.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")

    client_to_add = await Client.create(
        first_name=client.first_name,
        last_name=client.last_name,
        sexe = client.sexe,
        phone=client.phone,
        email=client.email,
        password=AuthService.get_password_hash(client.password),
        pays=client.pays,
        # preferences=client.preferences,
        account_status=client.account_status,
    )

    return {"message": "Utilisateur enregistré",
            "client" : client_to_add
        }

@router.get("")
async def get_all_users():
    clients = await Client.all()
    return clients

@router.get("/recent/{days_}")
async def get_recent_clients(days_ : int):
    thirty_days_ago = datetime.now() - timedelta(days=days_)
    clients = await Client.filter(created_at__gte=thirty_days_ago).all()
    count = await Client.filter(created_at__gte=thirty_days_ago).count()

    return {
        "message": "Clients enregistrés dans les 30 derniers jours",
        "clients": clients,
        "nombre": count
    }

@router.get("/{id_}")
async def getById(id_ : int):
    clientToGet = await Client.get_or_none(id = id_)
    if not clientToGet:
        return {
            "message" : "Client inexistant"
        }
        
    return {
        "message" : f"voici le client de id : {id_}",
        "client" : clientToGet
    }

@router.get("/nombre/total")
async def getNbrClient():
    nbr = await Client.all().count()
    return {
        "message" : "voici le nombre de clients",
        "nombre" : nbr
    }

@router.put("/{id_}")
async def updateClient(id_ :  int, item : Client_Create):
    clientToEdit = await Client.get_or_none(id = id_)
    if not clientToEdit:
        return {
            "message" : "Client inexistant"
        }
    clientToEdit.first_name = item.first_name
    clientToEdit.last_name =  item.last_name
    clientToEdit.phone = item.phone
    clientToEdit.email = item.email
    clientToEdit.sexe = item.sexe
    clientToEdit.password = item.password
    clientToEdit.pays = item.pays
    # clientToEdit.preferences = item.preferences
    clientToEdit.account_status = AccountStatus.ACTIVE
    
    await clientToEdit.save()
    return {
        "message" : "Information modifier avec succes",
        "client" : clientToEdit
    }

@router.delete("/{id_}")
async def delClient(id_ : int):
    clientToDel = await Client.get_or_none(id = id_)
    if not clientToDel:
        return {
            "message" : "Client inexistant"
        }
    await clientToDel.delete()
    return {
        "message": "effacer"
    }
    
#-------- get par pays

@router.get("/pays/nombres")
async def get_nombre_client_par_pays():
    resultats = await Client.all().group_by("pays").annotate(total=Count("id")).values("pays", "total")
    return {
        "message": "Nombre de clients par pays",
        "par_pays": resultats
    }

@router.get("/client/top")
async def get_top_cleintByPays():
    resultats = await (
        Client
        .all()
        .group_by("pays")
        .annotate(total=Count("id"))
        .order_by("-total")
        .limit(3)
        .values("pays", "total")
    )

    return {
        "message": "Top 3 pays par nombre Client",
        "top_villes": resultats
    }
    
@router.get("/top3/recents")
async def etablissements_recents():
    clients = await (
        Client
        .all()
        .order_by("-created_at")
        .limit(3)
        .values("id", "last_name", "first_name", "pays", "created_at")
    )

    return {
        "message": "3 derniers établissements ajoutés",
        "etablissements": clients
    }