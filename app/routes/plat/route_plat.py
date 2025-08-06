from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.plat import Plat
from app.models.etablissement import Etablissement
import os
from uuid import uuid4
import json
from app.enum.type_plat import Type_plat
from app.websocket.notification_manager import notification_manager
from app.models.notification import Notification


UPLOAD_DIR = "uploads/plat"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("/etablissement/{etablissement_id}")
async def getAllFood(etablissement_id: int):
    plats = await Plat.filter(etablissement_id=etablissement_id).all().order_by("-id")
    result = []
    for plat in plats:
        result.append({
            "id": plat.id,
            "etablissement_id": etablissement_id,
            "libelle": plat.libelle,
            "type_": plat.type,
            "image": f"uploads/plat/{os.path.basename(plat.image_url)}" if plat.image_url else None,
            "note": plat.note,
            "prix": plat.prix,
            "ingredients": plat.ingredients,
            "tags": plat.tags,
            "disponible": plat.disponible,
            "calories": plat.calories,
            "prep_minute": plat.prep_minute,
            "description" : plat.description
        })

    return {
        "message": "Voici la liste des plats",
        "plats": result
    }


@router.post("")
async def addPlatWithImage(
    libelle: str = Form(...),
    type_: Type_plat = Form(Type_plat.AUTRE),
    description: str = Form(...),
    note: int = Form(...),
    prix: int = Form(...),
    ingredients: str = Form(...),
    etablissement_id: int = Form(...),
    disponible: bool = Form(True),
    tags: str = Form("[]"),
    calories: int = Form(500),
    prep_minute: int = Form(15),
    image: UploadFile = File(...)
):
    etab = await Etablissement.get_or_none(id=etablissement_id)
    if not etab:
        return {"message": "Établissement introuvable"}

    if etab.type_ not in ["Hotelerie et Restauration", "Restauration"]:
        return {"message": "L'établissement n'est pas un restaurant"}

    if note > 5 or note < 0:
        return {"message": "Note invalide (0-5)"}

    if not image.content_type.startswith("image/"):
        return {"message": "Fichier image invalide"}

    filename = f"{uuid4().hex}_{image.filename}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as f:
        f.write(await image.read())

    try:
        ingredients_data = (
            json.loads(ingredients)
            if ingredients.strip().startswith("[")
            else [i.strip() for i in ingredients.split(",")]
        )
        tags_data = (
            json.loads(tags)
            if tags.strip().startswith("[")
            else [t.strip() for t in tags.split(",")]
        )
    except Exception as e:
        return {"message": "Erreur de parsing JSON", "debug": str(e)}

    plat = await Plat.create(
        libelle=libelle,
        type=type_,
        image_url=image_path,
        description=description,
        note=note,
        prix=prix,
        ingredients=ingredients_data,
        tags=tags_data,
        disponible=disponible,
        calories=calories,
        prep_minute=prep_minute,
        etablissement_id=etablissement_id
    )

    await Notification.create(
    message=f"Le plat « {plat.libelle} » a été ajouté.",
    lu=False,
    etablissement= await plat.etablissement
    )

    await notification_manager.broadcast(
        event="plat_create",
        payload={"message": f"Le plat « {plat.libelle} » a été ajouté."}
    )


    return {
        "message": "Plat créé avec succès avec image",
        "plat": {
            "id": plat.id,
            "libelle": plat.libelle,
            "image": f"uploads/plat/{filename}"
        }
    }


@router.put("/{id_plat}")
async def editPlat(
    id_plat: int,
    libelle: str = Form(...),
    type_: Type_plat = Form(Type_plat.AUTRE),
    description: str = Form(...),
    note: int = Form(...),
    prix: int = Form(...),
    ingredients: str = Form(...),
    tags: str = Form("[]"),
    disponible: bool = Form(True),
    calories: int = Form(500),
    prep_minute: int = Form(15),
    image: UploadFile = File(None)
):
    plat = await Plat.get_or_none(id=id_plat)
    if not plat:
        return {"message": "Plat introuvable"}

    if note > 5 or note < 0:
        return {"message": "Note invalide"}

    try:
        ingredients_data = (
            json.loads(ingredients)
            if ingredients.strip().startswith("[")
            else [i.strip() for i in ingredients.split(",")]
        )
        tags_data = (
            json.loads(tags)
            if tags.strip().startswith("[")
            else [t.strip() for t in tags.split(",")]
        )
    except Exception as e:
        return {"message": "Erreur dans les données JSON", "debug": str(e)}

    # Remplacement image
    if image:
        if not image.content_type.startswith("image/"):
            return {"message": "Fichier image invalide"}

        if plat.image_url and os.path.exists(plat.image_url):
            try:
                os.remove(plat.image_url)
            except Exception as e:
                print(f"Erreur suppression ancienne image : {e}")

        filename = f"{uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)

        with open(image_path, "wb") as f:
            f.write(await image.read())

        plat.image_url = image_path

    plat.libelle = libelle
    plat.type = type_
    plat.description = description
    plat.note = note
    plat.prix = prix
    plat.ingredients = ingredients_data
    plat.tags = tags_data
    plat.disponible = disponible
    plat.calories = calories
    plat.prep_minute = prep_minute

    await plat.save()
    
    
    await Notification.create(
    message=f"Le plat « {plat.libelle} » a été mis a jour.",
    lu=False,
    etablissement= await plat.etablissement
    )

    await notification_manager.broadcast(
        event="plat_update",
        payload={"message": f"Le plat « {plat.libelle} » a été mis a jour."}
    )

    return {
        "message": "Plat modifié avec succès",
        "plat": {
            "id": plat.id,
            "libelle": plat.libelle,
            "image": f"uploads/plat/{os.path.basename(plat.image_url)}" if plat.image_url else None
        }
    }


@router.delete("/{id_plat}")
async def deletePlat(id_plat: int):
    plat = await Plat.get_or_none(id=id_plat)
    if not plat:
        return {"message": "Plat introuvable"}

    if plat.image_url and os.path.exists(plat.image_url):
        try:
            os.remove(plat.image_url)
        except Exception as e:
            print(f"Erreur suppression image : {e}")

    
    await Notification.create(
    message=f"Le plat « {plat.libelle} » a été effacer.",
    lu=False,
    etablissement= await plat.etablissement
    )

    await notification_manager.broadcast(
        event="plat_delete",
        payload={"message": f"Le plat « {plat.libelle} » a été ajouté."}
    )
    await plat.delete()
    
    return {"message": "Plat supprimé avec succès"}

@router.delete("/etablissement/{etab_id}/{id_plat}")
async def delete_plat_from_etab(etab_id: int, id_plat: int):
    etab = await Etablissement.get_or_none(id=etab_id)
    if not etab:
        return {"message": "Établissement introuvable"}

    plat = await Plat.get_or_none(id=id_plat, etablissement=etab)
    if not plat:
        return {"message": "Plat introuvable dans cet établissement"}

    await plat.delete()
    return {"message": f"Plat (ID: {id_plat}) supprimé avec succès de l'établissement {etab_id}"}
