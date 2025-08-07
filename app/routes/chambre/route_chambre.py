from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.models.chambre import Chambre
from app.models.etablissement import Etablissement
from app.enum.etat_chambre import EtatChambre
from app.enum.room_type import TypeChambre
from decimal import Decimal
import os
import json
from uuid import uuid4
from typing import Optional
from app.websocket.notification_manager import notification_manager
from app.models.notification import Notification

router = APIRouter()
UPLOAD_DIR = "uploads/chambres"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.models.chambre import Chambre
from app.models.etablissement import Etablissement
from app.enum.etat_chambre import EtatChambre
from app.enum.room_type import TypeChambre
from decimal import Decimal
import os
import json
from uuid import uuid4
from typing import Optional

router = APIRouter()
UPLOAD_DIR = "uploads/chambres"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def ajouter_chambre(
    numero: str = Form(...),
    capacite: int = Form(...),
    equipements: str = Form(...),  # JSON string or comma-separated
    categorie: TypeChambre = Form(...),
    tarif: Decimal = Form(...),
    description: Optional[str] = Form("Une chambre idéale pour une famille de 4 personnes"),
    id_etablissement: int = Form(...),
    image: Optional[UploadFile] = File(None)
):
    etab = await Etablissement.get_or_none(id=id_etablissement)
    if not etab:
        return JSONResponse(status_code=404, content={"message": "Établissement introuvable"})

    if etab.type_ not in ["Hotelerie", "Hotelerie et Restauration"]:
        return JSONResponse(status_code=400, content={"message": "Cet établissement ne peut pas avoir de chambres"})

    # Parse equipements en JSON ou liste simple
    try:
        if equipements.strip().startswith("["):
            equipements_data = json.loads(equipements)
            if not isinstance(equipements_data, list):
                raise ValueError()
        else:
            equipements_data = [e.strip() for e in equipements.split(",") if e.strip()]
    except Exception:
        return JSONResponse(status_code=422, content={"message": "Le champ 'equipements' doit être un tableau JSON valide ou une liste séparée par des virgules"})

    image_path = None
    if image:
        if not image.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"message": "Fichier image invalide"})
        filename = f"{uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())
    else:
        image_path = "https://www.domainedarondeau.com/wp-content/uploads/2017/06/Hotel-7-large-2.jpg"

    chambre = await Chambre.create(
        numero=numero,
        capacite=capacite,
        equipements=equipements_data,
        categorie=categorie,
        tarif=tarif,
        description=description,
        photo_url=image_path,
        etat=EtatChambre.LIBRE,
        etablissement=etab
    )
    
    
    await Notification.create(
    message=f"La chambre N°{chambre.numero} a été ajoutée.",
    lu=False,
    etablissement=chambre.etablissement
    )


    await notification_manager.send_to_etablissement(
        etablissement_id= chambre.etablissement_id,
        event="chambre_create",
        payload={"message": f"Le chambre numero « {chambre.numero} » a été ajouté."}
    )

    return {
        "messgae" : "chambre ajouter avec succes",
        "chambre" : chambre
    }


@router.put("/{id_chambre}")
async def update_chambre(
    id_chambre: int,
    numero: str = Form(...),
    capacite: int = Form(...),
    equipements: str = Form(...),
    categorie: TypeChambre = Form(...),
    tarif: Decimal = Form(...),
    description: str = Form(...),
    id_etablissement: int = Form(...),
    image: Optional[UploadFile] = File(None)
):
    chambre = await Chambre.get_or_none(id=id_chambre)
    if not chambre:
        return JSONResponse(status_code=404, content={"message": "Chambre introuvable"})

    etab = await Etablissement.get_or_none(id=id_etablissement)
    if not etab:
        return JSONResponse(status_code=404, content={"message": "Établissement introuvable"})

    if etab.type_ not in ["Hotelerie", "Hotelerie et Restauration"]:
        return JSONResponse(status_code=400, content={"message": "Cet établissement ne peut pas avoir de chambres"})

    try:
        if equipements.strip().startswith("["):
            equipements_data = json.loads(equipements)
            if not isinstance(equipements_data, list):
                raise ValueError()
        else:
            equipements_data = [e.strip() for e in equipements.split(",") if e.strip()]
    except Exception:
        return JSONResponse(status_code=422, content={"message": "Le champ 'equipements' doit être un tableau JSON valide ou une liste séparée par des virgules"})

    chambre.numero = numero
    chambre.capacite = capacite
    chambre.equipements = equipements_data
    chambre.categorie = categorie
    chambre.tarif = tarif
    chambre.description = description
    chambre.etablissement = etab

    if image:
        if not image.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"message": "Fichier image invalide"})

        if chambre.photo_url and os.path.exists(chambre.photo_url) and not chambre.photo_url.startswith("http"):
            try:
                os.remove(chambre.photo_url)
            except Exception as e:
                print(f"Erreur suppression image : {e}")

        filename = f"{uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        chambre.photo_url = image_path

    await chambre.save()
    
    
    await Notification.create(
    message=f"La chambre N°{chambre.numero} a été mise à jour.",
    lu=False,
    etablissement=chambre.etablissement
    )

    await notification_manager.send_to_etablissement(
        etablissement_id= chambre.etablissement_id,
        event="chambre_update",
        payload={"message": f"Le chambre numero « {chambre.numero} » a été modifier."}
    )


    return JSONResponse(status_code=200, content={
        "message": f"Chambre {id_chambre} modifiée avec succès",
        "chambre": {
            "id": chambre.id,
            "numero": chambre.numero,
            "photo_url": chambre.photo_url,
        }
    })


@router.get("")
async def get_all_chambres():
    
    chambres = await Chambre.all().order_by("-id")
    return {"message": "Toutes les chambres", "chambres": chambres}


@router.get("/{id_chambre}")
async def get_chambre_by_id(id_chambre: int):
    chambre = await Chambre.get_or_none(id=id_chambre)
    if not chambre:
        return JSONResponse(status_code=404, content={"message": "Chambre introuvable"})
    return {"message": "Chambre trouvée", "chambre": chambre}


@router.get("/etablissement/{id_etab}")
async def get_chambres_etablissement(id_etab: int):
    chambres = await Chambre.filter(etablissement_id=id_etab)
    return {"message": f"Liste des chambres de l'établissement {id_etab}", "chambres": chambres}


@router.get("/nombre/{id_}")
async def get_nbr_chambre_by_etab(id_: int):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return JSONResponse(status_code=404, content={"message": "Établissement introuvable"})
    count = await Chambre.filter(etablissement_id=id_).count()
    return {"message": "Nombre total de chambres", "nombre": count}


@router.get("/libre/{id_}")
async def get_all_chambre_libre(id_: int):
    etab = await Etablissement.get_or_none(id=id_)
    if not etab:
        return JSONResponse(status_code=404, content={"message": "Établissement introuvable"})
    libres = await Chambre.filter(etablissement_id=etab.id, etat=EtatChambre.LIBRE).all().order_by("-id")
    return {"message": f"Chambres libres de {etab.nom}", "chambres": libres}


@router.delete("/{id_chambre}")
async def delete_chambre(id_chambre: int):
    chambre = await Chambre.get_or_none(id=id_chambre)
    if not chambre:
        return JSONResponse(status_code=404, content={"message": "Chambre introuvable"})

    if chambre.photo_url and os.path.exists(chambre.photo_url):
        try:
            os.remove(chambre.photo_url)
        except Exception as e:
            print(f"Erreur suppression image : {e}")
            
    num = chambre.numero
    etab = await chambre.etablissement
    
    
    await Notification.create(
    message=f"La chambre N°{num} a été supprimée.",
    lu=False,
    etablissement=etab
    )
    
    await notification_manager.send_to_etablissement(
        etablissement_id= chambre.etablissement_id,
        event="chambre_delete",
        payload={"message": f"Le chambre numero « {chambre.numero} » a été effacer."}
    )     

    await chambre.delete()
    
    

    
    return {"message": "Chambre supprimée avec succès"}
