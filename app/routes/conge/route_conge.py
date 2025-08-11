from fastapi import APIRouter, HTTPException
from app.models.conge import Conge
from app.models.etablissement import Etablissement
from app.models.personnel import Personnel
from app.schemas.conge_create import Conger_Create, Conger_Patch_status
from app.enum.conge_status import CongerStatus
router = APIRouter()


@router.get("")
async def getALlconger():
    allConger = await Conge.all().select_related("personnel")
    return {
        "message": "Voici la liste des Congés (All)",
        "conges": allConger
    }


@router.get("/personnel/{id_}")
async def getCongeByPersonnel(id_: int):
    personnel_ = await Personnel.get_or_none(id=id_)
    if not personnel_:
        return {
            "message": "Personnel introuvable"
        }

    conges_ = await Conge.filter(personnel=personnel_).select_related("personnel")
    return {
        "message": f"Voici la liste des Congés du personnel : {personnel_.nom} {personnel_.prenom}",
        "conges": conges_
    }


@router.get("/etablissement/{id_}")
async def getCongeByEtablissement(id_: int):
    etab_ = await Etablissement.get_or_none(id=id_)
    if not etab_:
        return {"message": "Établissement introuvable"}

    conges = await Conge.filter(personnel__etablissement=etab_).select_related("personnel")
    return {
        "message": f"Voici la liste des congés dans l'établissement {etab_.nom}",
        "conges": conges
    }

@router.patch("/{id_conge}/{status}")
async def patch_Status(id_conge : int, status : CongerStatus = CongerStatus.REFUSER ):
    conge = await Conge.get_or_none(id = id_conge)
    if not conge:
        return {
            "message" : "Conger introuvable"
        }
    conge.status = status
    
    await conge.save()
    
    return {
        "message" : "Conge patcher avec succes",
        "conge" : conge
    }

@router.post("")
async def createConger(data: Conger_Create):
    personnel = await Personnel.get_or_none(id=data.personnel_id)
    etablissement = await Etablissement.get_or_none(id=data.etablissement_id)

    if not personnel:
        return {"message": "Personnel introuvable"}

    if not etablissement:
        return {"message": "Établissement introuvable"}

    # Optionnel : vérifier que le personnel appartient à l’établissement
    if personnel.etablissement_id != etablissement.id:
        return {"message": "Ce personnel n'appartient pas à cet établissement"}

    conge = await Conge.create(
        type=data.type,
        status=data.status,
        dateDebut=data.dateDebut,
        dateDmd=data.dateDmd,
        dateFin=data.dateFin,
        raison=data.raison,
        fichierJoin=data.fichierJoin,
        personnel=personnel
    )

    return {
        "message": f"Congé créé pour {personnel.nom} {personnel.prenom}",
        "conge": conge
    }


@router.delete("/{id_}")
async def deleteConge(id_: int):
    conge_to_del = await Conge.get_or_none(id=id_)
    if not conge_to_del:
        return {"message": "Congé introuvable"}

    await conge_to_del.delete()
    return {"message": "Congé effacé avec succès"}
