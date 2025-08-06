from itertools import count
from tortoise.functions import Count
from fastapi import Form, File, UploadFile, HTTPException, APIRouter
from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.schemas.etablissementCreate import EtablissementCreate, EtabStatus
from app.services.auth_service import AuthService
from app.services.email_service import send_email
from datetime import datetime, timedelta
from app.enum.account_status import AccountStatus
#from passlib.hash import bcrypt
from app.services.auth_service import AuthService
from app.enum.type_etablissement import Type_etablissement
from app.enum.etablissement_statu import Etablissement_status
from typing import Optional


import os
from uuid import uuid4
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads/etablissement"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def addEtablissement(
    nom: str = Form(...),
    adresse: str = Form(...),
    ville: str = Form(...),
    pays: str = Form(...),
    email: str = Form(...),
    mot_de_passe: str = Form(...),
    type_: Type_etablissement = Form(...),
    code_postal: Optional[str] = Form(None),
    telephone: Optional[str] = Form(None),
    site_web: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    statut: Etablissement_status = Form(Etablissement_status.INACTIVE),
    logo: UploadFile = File(None),
):
    data = {
        "nom": nom,
        "adresse": adresse,
        "ville": ville,
        "pays": pays,
        "email": email,
        "mot_de_passe": AuthService.get_password_hash(mot_de_passe),
        "type_": type_,
        "code_postal": code_postal,
        "telephone": telephone,
        "site_web": site_web,
        "description": description,
        "statut": statut,
    }

    if logo:
        if not logo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Le fichier logo doit être une image valide.")

        filename = f"{uuid4().hex}_{logo.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        data["logo"] = f"uploads/etablissement/{filename}"

    etabCreate = await Etablissement.create(**data)

    return {
        "message": "Établissement ajouté avec succès",
        "etablissement": etabCreate
    }

@router.get("/recent/{days_}")
async def getRecentEtablissements(days_ : int):
    thirty_days_ago = datetime.now() - timedelta(days=days_)
    etabs = await Etablissement.filter(created_at__gte=thirty_days_ago).all().order_by("-id")
    count = await Etablissement.filter(created_at__gte=thirty_days_ago).count()

    return {
        "message": "Établissements créés dans les 30 derniers jours",
        "etablissements": etabs,
        "nombres": count
    }

@router.delete("/{id_}")
async def deleteEtablissement(id_: int):
    etab = await Etablissement.get_or_none(id=id_).prefetch_related("chambres")
    if not etab:
        return {"message": "Établissement introuvable"}

    await Chambre.filter(etablissement_id=id_).delete()

    if etab.logo:
        logo_path = etab.logo.lstrip("/")
        if os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except Exception as e:
                return {
                    "message": "Erreur lors de la suppression de l'image",
                    "erreur": str(e)
                }
    await etab.delete()

    return {"message": "Établissement supprimé avec succès"}



@router.put("/status/{id_}")
async def editStatusAccountEtablissement(id_ : int, item : EtabStatus):
    etab_ = await Etablissement.get_or_none(id = id_)
    if not etab_:
        return {"message" : "Etab inexistant"}
    etab_.statut = item.statut
    await etab_.save()
    return {
        "message" : "Etablissement account status edited",
        "Etablissement" : etab_
    }


@router.put("/{id_}")
async def editEtablissement(
    id_: int,
    nom: str = Form(...),
    adresse: str = Form(...),
    ville: str = Form(...),
    pays: str = Form(...),
    email: str = Form(...),
    mot_de_passe: Optional[str] = Form(None),
    type_: Type_etablissement = Form(...),
    code_postal: Optional[str] = Form(None),
    telephone: Optional[str] = Form(None),
    site_web: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    statut: Etablissement_status = Form(...),
    logo: UploadFile = File(None),
):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return {"message": "Établissement introuvable"}

    etab.nom = nom
    etab.adresse = adresse
    etab.ville = ville     
    etab.pays = pays
    etab.code_postal = code_postal
    etab.telephone = telephone
    etab.email = email
    etab.site_web = site_web
    etab.description = description
    etab.type_ = type_
    etab.statut = statut

    if mot_de_passe:
        etab.mot_de_passe = AuthService.get_password_hash(mot_de_passe)

    if logo:
        if not logo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Fichier logo invalide (doit être une image)")

        if etab.logo:
            old_path = etab.logo.lstrip("/")
            if os.path.exists(old_path):
                os.remove(old_path)

        filename = f"{uuid4().hex}_{logo.filename}"
        new_logo_path = os.path.join(UPLOAD_DIR, filename)

        with open(new_logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        etab.logo = f"uploads/etablissement/{filename}"

    await etab.save()

    return {"message": "Modification réussie", "etablissement": etab}


@router.get("")
async def getAllEtablissement():
    allEtab = await Etablissement.all().order_by("-id")
    return {
        "message" : "Voici la liste de Etablissement",
        "etablissements" : allEtab
    }


@router.get("/{id_}")
async def getOneEtablissement(id_: int):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return {"message": "Établissement introuvable"}
    return etab

# get status , nombre , par ville , pays 

@router.get("/nombre/Active")
async def getEtabActive():
    query = Etablissement.filter(statut="Activer")
    etabs = await query.all()
    count = await query.count()
    return {
        "message": "Voici la liste des établissements actifs",
        "etablissements": etabs,
        "nombres": count
    }

@router.get("/nombre/Inactive")
async def getEtabInactive():
    query = Etablissement.filter(statut="Inactive")
    etabs = await query.all()
    count = await query.count()
    return {
        "message": "Voici la liste des établissements inactifs",
        "etablissements": etabs,
        "nombres": count
    }

@router.get("/ville/{ville_nom}")
async def getEtablissementByVille(ville_nom: str):
    query = Etablissement.filter(ville=ville_nom)
    etabs = await query.all()
    count = await query.count()
    return {
        "message": f"Voici la liste des établissements de la ville de {ville_nom}",
        "etablissements": etabs,
        "nombres": count
    }
    

@router.get("/nombre/total")
async def get_nbr_total():
    nombre = await Etablissement.all().count()
    return {
        "message": "Voici le nombre total des établissements.",
        "nombre": nombre
    }


@router.get("/pays/nombres")
async def get_nombre_etablissements_par_pays():
    resultats = await Etablissement.all().group_by("pays").annotate(total=Count("id")).values("pays", "total")
    return {
        "message": "Nombre d'établissements par pays",
        "par_pays": resultats
    }

@router.get("/taux/occupation")
async def getTauxOccupation():
    # actif / total
    etabActifNbr = await Etablissement.filter(statut = "Activer").count()
    etabTotalNumber = await Etablissement.all().count()
    print(etabActifNbr)
    print(etabTotalNumber)
    taux = round((etabActifNbr * 100.00) / etabTotalNumber, 2) 
    
    return {
        "message" : "voici le taux du ...",
        "nombre" : f"{taux}"
    }

    # HOTELERIE = "Hotelerie"
    # RESTAURATION = "Restauration"
    # HOTELERIE_RESTAURATION = "Hotelerie et Restauration"

@router.get("/nombre/nombre-type")
async def getByTyNbr():
    nbrHotelerie = await Etablissement.filter(type_ = "Hotelerie").count()
    nbrRestaurant = await Etablissement.filter(type_ = "Restauration").count()
    nbrRestaurantAndHotel = await Etablissement.filter(type_ = "Hotelerie et Restauration").count()
    
    return {
        "message" : "voici les nbr by Type",
        "nombre_hotelerie" : nbrHotelerie,
        "nombre_restauration" : nbrRestaurant,
        "nombre_restauration_hotelerie" : nbrRestaurantAndHotel,
        
    }
    
    
@router.get("/villes/top")
async def get_top_villes():
    resultats = await (
        Etablissement
        .all()
        .group_by("ville")
        .annotate(total=Count("id"))
        .order_by("-total")
        .limit(3)
        .values("ville", "total")
    )

    return {
        "message": "Top 3 villes par nombre d'établissements",
        "top_villes": resultats
    }
    
@router.get("/pays/top")
async def get_top_pays():
    resultats = await (
        Etablissement
        .all()
        .group_by("pays")
        .annotate(total=Count("id"))
        .order_by("-total")
        .limit(3)
        .values("pays", "total")
    )

    return {
        "message": "Top 3 pays par nombre d'établissements",
        "top_villes": resultats
    }

@router.get("/taux/croissance")
async def taux_de_croissance_mensuel():
    now = datetime.now()
    start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    last_month = (start_of_current_month - timedelta(days=1)).replace(day=1)

    etablissements_actuels = await Etablissement.filter(
        created_at__gte=start_of_current_month,
        created_at__lt=now
    ).count()

    etablissements_precedents = await Etablissement.filter(
        created_at__gte=last_month,
        created_at__lt=start_of_current_month
    ).count()

    if etablissements_precedents == 0:
        croissance = 100 if etablissements_actuels > 0 else 0
    else:
        croissance = ((etablissements_actuels - etablissements_precedents) / etablissements_precedents) * 100

    return {
        "message": "Taux de croissance mensuel",
        "mois_precedent": etablissements_precedents,
        "mois_courant": etablissements_actuels,
        "taux_de_croissance": round(croissance, 2)
    }
    
@router.get("/top3/recents")
async def etablissements_recents():
    etablissements = await (
        Etablissement
        .all()
        .order_by("-created_at")
        .limit(3)
        .values("id", "nom", "ville", "pays", "created_at")
    )

    return {
        "message": "3 derniers établissements ajoutés",
        "etablissements": etablissements
    }