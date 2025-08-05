from fastapi import APIRouter, Body
from app.models.product import Produit
from app.schemas.product_create import Product_Create
from app.models.mouvement_stock import MouvementStock
from app.models.etablissement import Etablissement
from app.models.personnel import Personnel
from app.enum.type_mouvement_stock import Type_mouvement_stock

router = APIRouter()

@router.get("")
async def getAllProduct():
    all_ = await Produit.all()
    return {
        "message" : "VOici lal lise",
        "produits" : all_
    }
    
@router.get("/etablissement/{id_etab}")
async def getByEtab(id_etab : int):
    etab_ = await Etablissement.get_or_none(id = id_etab)
    if not etab_:
        return {
            "message" : "Etablissement inexistante"
        }
    
    all_ByEtab = await Produit.filter(etablissement = etab_).all()
    
    return {
        "message" : "voici la liste de",
        "produits" : all_ByEtab
    }

@router.post("")
async def addProduit(item : Product_Create):
    etab_ = await Etablissement.get_or_none(id = item.etablissement_id)
    
    if not etab_:
        return {
            "message" : "Etablissement inexistante"
        }
    pers_ = await Personnel.get_or_none(id = item.personnel_id)
    
    if not pers_:
        return {
            "message" : "Etablissement inexistante"
        }
        
    productToAdd = await Produit.create(
        nom = item.nom,
        quantite = item.quantite,
        prix = item.prix,
        seuil_stock = item.seuil_stock,
        etablissement = etab_ 
    )
    
    await MouvementStock.create(
        produit = productToAdd,
        personnel = pers_,
        quantite = productToAdd.quantite,
        type = Type_mouvement_stock.ENTRE,
        raison = "Stock initiale "
    )
    
    return {
        "message" : "produit ajouter avec succes",
        "produit" : productToAdd
    }

@router.delete("/{id_}")
async def deletePro(id_ : int):
    pro_ = await Produit.get_or_none(id = id_)
    if not pro_:
        return {"message" : "Kozjfef"}
    
    await pro_.delete()
    return {
        "message" : "effacer avec succes"
    }
    
    
@router.put("/{id_}")
async def editProd(id_ : int, item : Product_Create):
    pro_ = await Produit.get_or_none(id = id_)
    if not pro_:
        return {"message" : "Kozjfef"}
    
    pro_.nom = item.nom,
    pro_.quantite = item.quantite,
    pro_.prix = item.prix,
    pro_.seuil_stock = item.seuil_stock,
    
    return {
        "message" : "modufiert"
    }
    
@router.patch("/{id_}")
async def editProd(id_ : int, quantite: int = Body(...), type : str = Body(...), personnel_id : int = Body(...)):
    pro_ = await Produit.get_or_none(id = id_)
    if not pro_:
        return {"message" : "Kozjfef"}
    
    
    pers_ = await Personnel.get_or_none(id = personnel_id)
    if not pers_:
        return {"message" : "Kozjfef"}
    
    
    if type == Type_mouvement_stock.ENTRE:
        pro_.quantite = pro_.quantite + quantite
        await MouvementStock.create(
        produit = pro_,
        personnel = pers_,
        quantite = quantite,
        type = Type_mouvement_stock.ENTRE,
        raison = "Stock initiale "
    )
    else:
        if pro_.quantite > quantite:
            pro_.quantite = pro_.quantite - quantite
        else: 
            pro_.quantite = quantite - pro_.quantite
        
        await MouvementStock.create(
        produit = pro_,
        personnel = pers_,
        quantite = quantite,
        type = Type_mouvement_stock.SORTIE,
        raison = "Stock initiale "
        
        )
    
    
    return {
        "message" : "modufiert",
        "produit" : pro_
    }
    


    