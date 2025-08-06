from fastapi import APIRouter
from app.models.superAdmin import SuperAdmin
from app.schemas.superAdminCreate import SuperAdminCreate
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("")
async def getSuperAdminAll():
    allSuper = await SuperAdmin.all().order_by("-id")
    return{
        "message" : "Voici les superAdmin",
        "SuperAdmins" : allSuper
    }

@router.post("")
async def addSuperAdmin(item : SuperAdminCreate):
    SuperAdminToAdd = await SuperAdmin.create(
        email = item.email,
        password = AuthService.get_password_hash(item.password)
    )
    
    return {
        "message" : "superadmin ajouter",
        "superAdmin" : SuperAdminToAdd
    }

@router.delete("/{id_}")
async def deleteSuperAdmin(id_ : int):
    superAdminToDel = await SuperAdmin.get_or_none(id = id_)
    if not superAdminToDel:
        return {
            "message" : "Super Admin Introuvable"
        }
    await superAdminToDel.delete()
    
    return {
        "message" : "superAdmin Supprimer"
    }