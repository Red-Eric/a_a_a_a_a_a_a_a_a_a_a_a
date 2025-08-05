from fastapi import APIRouter, HTTPException
from app.models.commande_plat import Commande_Plat
from app.schemas.commande_plat_create import Commande_plat_create
from app.models.client import Client
from app.models.plat import Plat
from app.models.etablissement import Etablissement

router = APIRouter()


@router.get("")
async def get_all_commande_plat():
    commandes = await Commande_Plat.all().prefetch_related("client", "plat")
    return {
        "message": "Voici la liste des commandes de plats",
        "commandes": commandes
    }


@router.post("")
async def add_commande_plat(item: Commande_plat_create):
    client = await Client.get_or_none(id=item.client_id)
    plat = await Plat.get_or_none(id=item.plat_id)

    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    if not plat:
        raise HTTPException(status_code=404, detail="Plat introuvable")


    commande = await Commande_Plat.create(
        client=client,
        plat=plat,
        montant=item.montant,
        quantite=item.quantite,
        description=item.description
        # L'attribut `etablissement` n’existe pas sur Commande_Plat, sauf si tu l’as oublié dans ton modèle
    )

    return {
        "message": "Commande ajoutée avec succès",
        "commande": commande
    }


@router.delete("/{id_}")
async def delete_commande_plat(id_: int):
    commande = await Commande_Plat.get_or_none(id=id_)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    await commande.delete()
    return {"message": "Commande supprimée avec succès"}
