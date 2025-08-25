from itertools import count
from tortoise.functions import Count
from fastapi import Form, File, UploadFile, HTTPException, APIRouter
from app.enum.commande_statu import CommandeStatu
from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.schemas.etablissementCreate import EtablissementCreate, EtabStatus
from app.services.auth_service import AuthService
from app.services.email_service import send_email
from datetime import datetime, timedelta, timezone
from app.enum.account_status import AccountStatus
#from passlib.hash import bcrypt
from app.services.auth_service import AuthService
from app.enum.type_etablissement import Type_etablissement
from app.enum.etablissement_statu import Etablissement_status
from typing import Optional
from app.models.reservation import Reservation
from app.models.commande_plat import Commande_Plat
from app.enum.status_reservation import Status_Reservation
from tortoise.functions import Sum
from app.models.personnel import Personnel
from collections import defaultdict

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
  


@router.get("/revenu/mois/{etab_id}/{date_str}")
async def get_revenue_mois(etab_id: int, date_str: str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m")
    except ValueError:
        return {"message": "Format de date invalide. Utiliser YYYY-MM (ex: 2012-01)"}

    debut_mois = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mois = (debut_mois + timedelta(days=32)).replace(day=1)

    etab_ = await Etablissement.get_or_none(id=etab_id)
    if not etab_:
        return {"message": "Etablissement introuvable"}

    nb_jours = (fin_mois - debut_mois).days
    resultats = [
        {
            "date": (debut_mois + timedelta(days=i)).strftime("%Y-%m-%d"),
            "revenu_reservation": 0.0,
            "revenu_commande_plat": 0.0,
            "revenu_total": 0.0
        }
        for i in range(nb_jours)
    ]

    reservations = await Reservation.filter(
        status=Status_Reservation.CONFIRMER,
        chambre__etablissement_id=etab_id,
        date_depart__gte=debut_mois,
        date_arrivee__lt=fin_mois
    ).prefetch_related('chambre')

    for res in reservations:
        if res.chambre and res.chambre.tarif:
            tarif_journalier = float(res.chambre.tarif)
            print(f"Reservation chambre_id={res.chambre.id} tarif_journalier={tarif_journalier}")
            arrivee = res.date_arrivee.replace(tzinfo=None).date()
            depart = res.date_depart.replace(tzinfo=None).date()
            start_day = max(arrivee, debut_mois.date())
            end_day = min(depart, (fin_mois - timedelta(seconds=1)).date())

            current_day = start_day
            while current_day < end_day:
                idx = (current_day - debut_mois.date()).days
                print(f"Ajout tarif pour date={current_day} idx={idx}")
                if 0 <= idx < nb_jours:
                    resultats[idx]["revenu_reservation"] += tarif_journalier
                current_day += timedelta(days=1)

    commandes = await Commande_Plat.filter(
        status=CommandeStatu.PAYEE,
        date__gte=debut_mois,
        date__lt=fin_mois
    ).all()

    for cmd in commandes:
        date_cmd = cmd.date.replace(tzinfo=None).date()
        idx = (date_cmd - debut_mois.date()).days
        print(f"Commande date={date_cmd} idx={idx} montant={cmd.montant} quantite={cmd.quantite}")
        if 0 <= idx < nb_jours:
            resultats[idx]["revenu_commande_plat"] += cmd.montant * cmd.quantite

    for jour in resultats:
        jour["revenu_total"] = jour["revenu_reservation"] + jour["revenu_commande_plat"]

    return {
        "mois": debut_mois.strftime("%B %Y"),
        "details": resultats
    }

# salaire 


@router.get("/salaire/personnel/{id_etab}")
async def getSalaireTotalEmployer(id_etab: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")

    result = await Personnel.filter(etablissement_id=id_etab).annotate(
        total_salaire=Sum("salaire")
    ).values("total_salaire")

    total = result[0]["total_salaire"] if result and result[0]["total_salaire"] is not None else 0

    return {
        "message" : "Voici la total des salaire",
        "total" : total
    }
    


@router.get("/bilan/etablissement/{id_etab}")
async def bilan_etablissement(id_etab: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")

    depenses_res = await Personnel.filter(etablissement_id=id_etab).annotate(
        total_salaire=Sum("salaire")
    ).values("total_salaire")
    total_salaire = depenses_res[0]["total_salaire"] if depenses_res and depenses_res[0]["total_salaire"] is not None else 0

    reservations = await Reservation.filter(
        status=Status_Reservation.CONFIRMER,
        chambre__etablissement_id=id_etab
    ).prefetch_related("chambre")

    revenu_reservations = sum(
        float(res.chambre.tarif) * res.duree
        for res in reservations if res.chambre and res.duree
    )

    commandes_res = await Commande_Plat.filter(
        status=CommandeStatu.PAYEE,
        plat__etablissement_id=id_etab
    ).annotate(total_montant=Sum("montant")).values("total_montant")

    revenu_commandes = commandes_res[0]["total_montant"] if commandes_res and commandes_res[0]["total_montant"] is not None else 0

    total_rentrant = revenu_reservations + revenu_commandes
    benefice = total_rentrant - total_salaire

    return {
        "message": "Bilan de l'établissement",
        "depenses": total_salaire,
        "rentrant": total_rentrant,
        "details": {
            "revenu_reservations": revenu_reservations,
            "revenu_commandes": revenu_commandes
        },
        "benefice": benefice
    }


# from collections import defaultdict


@router.get("/bilan/etablissement/{id_etab}/{annee}")
async def bilan_etablissement_annuel(id_etab: int, annee: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")

    depenses_res = await Personnel.filter(etablissement_id=id_etab).annotate(
        total_salaire=Sum("salaire")
    ).values("total_salaire")
    salaire_total = depenses_res[0]["total_salaire"] if depenses_res and depenses_res[0]["total_salaire"] is not None else 0

    bilan_mensuel = {}
    for mois in range(1, 13):
        cle = f"{annee}-{mois:02d}"
        bilan_mensuel[cle] = {
            "depenses": salaire_total,
            "revenu": 0,
            "details": {
                "revenu_reservations": 0,
                "revenu_commandes": 0
            },
            "benefice": 0
        }

    reservations = await Reservation.filter(
        status=Status_Reservation.CONFIRMER,
        chambre__etablissement_id=id_etab,
        date_arrivee__year=annee
    ).prefetch_related("chambre")

    for res in reservations:
        if res.chambre and res.duree:
            mois_cle = res.date_arrivee.strftime("%Y-%m")
            montant = float(res.chambre.tarif) * res.duree
            bilan_mensuel[mois_cle]["revenu"] += montant
            bilan_mensuel[mois_cle]["details"]["revenu_reservations"] += montant

    commandes = await Commande_Plat.filter(
        status=CommandeStatu.PAYEE,
        plat__etablissement_id=id_etab,
        date__year=annee
    ).prefetch_related("plat")

    for cmd in commandes:
        mois_cle = cmd.date.strftime("%Y-%m")
        montant = float(cmd.montant)
        bilan_mensuel[mois_cle]["revenu"] += montant
        bilan_mensuel[mois_cle]["details"]["revenu_commandes"] += montant

    for mois, data in bilan_mensuel.items():
        data["benefice"] = data["revenu"] - data["depenses"]

    return {
        "message": f"voici le bilan de cette année {annee}",
        "bilan": dict(sorted(bilan_mensuel.items()))
    }


@router.get("/bilan/tout/{id_etab}")
async def bilan_etablissement_tous_les_ans(id_etab: int):
    etab = await Etablissement.get_or_none(id=id_etab)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")

    # Total salaire fixe par année (dépenses)
    depenses_res = await Personnel.filter(etablissement_id=id_etab).annotate(
        total_salaire=Sum("salaire")
    ).values("total_salaire")
    salaire_total = depenses_res[0]["total_salaire"] if depenses_res and depenses_res[0]["total_salaire"] is not None else 0

    bilan_annuel = {}

    # ---- RÉSERVATIONS ----
    reservations = await Reservation.filter(
        status=Status_Reservation.CONFIRMER,
        chambre__etablissement_id=id_etab
    ).prefetch_related("chambre")

    for res in reservations:
        if res.chambre and res.duree and res.date_arrivee:
            annee = res.date_arrivee.year
            montant = float(res.chambre.tarif) * res.duree

            if annee not in bilan_annuel:
                bilan_annuel[annee] = {
                    "depenses": salaire_total,
                    "revenu": 0,
                    "details": {
                        "revenu_reservations": 0,
                        "revenu_commandes": 0
                    },
                    "benefice": 0
                }

            bilan_annuel[annee]["revenu"] += montant
            bilan_annuel[annee]["details"]["revenu_reservations"] += montant

    # ---- COMMANDES ----
    commandes = await Commande_Plat.filter(
        status=CommandeStatu.PAYEE,
        plat__etablissement_id=id_etab
    ).prefetch_related("plat")

    for cmd in commandes:
        if cmd.date:
            annee = cmd.date.year
            montant = float(cmd.montant)

            if annee not in bilan_annuel:
                bilan_annuel[annee] = {
                    "depenses": salaire_total,
                    "revenu": 0,
                    "details": {
                        "revenu_reservations": 0,
                        "revenu_commandes": 0
                    },
                    "benefice": 0
                }

            bilan_annuel[annee]["revenu"] += montant
            bilan_annuel[annee]["details"]["revenu_commandes"] += montant

    # ---- BENEFICE ----
    for annee, data in bilan_annuel.items():
        data["benefice"] = data["revenu"] - data["depenses"]

    return {
        "message": "voici le bilan annuel global",
        "bilan": dict(sorted(bilan_annuel.items()))
    }
