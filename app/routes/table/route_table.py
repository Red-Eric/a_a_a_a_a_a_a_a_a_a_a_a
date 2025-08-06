from fastapi import APIRouter
from app.models.table import Table
from app.schemas.table_create import Table_create
from app.models.etablissement import Etablissement
from app.models.client import Client
from app.enum.type_etablissement import Type_etablissement
from app.enum.status_table import status_table

router = APIRouter()

@router.get("")
async def getAllTable():
    all_ = await Table.all().order_by("-id")
    return {
        "message" : "Voici la liste de tout les table dans la DB",
        "tables" : all_
    }

@router.delete("/{id_}")
async def deleteTable(id_ : int):
    tab_ = await Table.get_or_none(id = id_)
    if not tab_:
        return {
            "message" : "table introuvable"
        }
    
    await tab_.delete()
    
    return {
        "message" : "Table effacer avec succes"
    }
    
@router.post("")
async def addtable(item : Table_create):
    etab_ = await Etablissement.get_or_none(id = item.etablissement_id)
    if not etab_:
        return {
            "message" : "etablissement introuvable"
        }
    if etab_.type_ == Type_etablissement.HOTELERIE:
        return {
            "message" : "L etablissement doit etre un restauration"
        }
        
    tab_ = await Table.create(
            nom = item.nom,
            status = item.status,
            type = item.status,
            positionX =  item.position.x,
            positionY = item.position.y,
            positionZ = item.position.z,
            rotationX = item.rotation.x,
            rotationY = item.rotation.y,
            rotationZ = item.rotation.z,
            etablissement= etab_,
        )
    return {
        "message" : "Une table a ete ajouter",
        "table" : tab_
    }

@router.put("/{id_}")
async def editTable(id_ : int, item : Table_create):
    table_ = await Table.get_or_none(id = id_)
    etab_ = await Etablissement.get_or_none(id = item.etablissement_id)
    if not etab_:
        return {
            "message" : "etablissement introuvable"
        }
    if not table_:
        return {
            "message" : "Table introuvable"
        }
    
    table_.nom = item.nom,
    table_.status = item.status,
    table_.type = item.status,
    table_.positionX =  item.position.x,
    table_.positionY = item.position.y,
    table_.positionZ = item.position.z,
    table_.rotationX = item.rotation.x,
    table_.rotationY = item.rotation.y,
    table_.rotationZ = item.rotation.z,
    table_.etablissement = etab_,
    
    await table_.save()
    return {
        "message" : "Table modifier avec succes",
        "table" : table_
    }
    
@router.put("/status/{status_}/{id_}")
async def changeStatustable(status_ : str , id_ : int):
    table_ = await Table.get_or_none(id = id_)
    if not table_:
        return {
            "message" : "Table introuvable"
        }
    
    table_.status = status_
    await table_.save()
    return {
        "message" : f"la status de la Table {table_.nom} a ete modifier",
        "table" : table_
    }