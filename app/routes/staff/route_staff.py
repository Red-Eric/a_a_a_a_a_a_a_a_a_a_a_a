from fastapi import HTTPException, APIRouter
from app.models.personnel import Personnel
from app.schemas.userCreate import User_Create
from app.enum.role import Role

router = APIRouter()

@router.post("/")
async def addUser(user: User_Create):
    # Vérifier si l'email existe déjà
    existing_user = await Personnel.get_or_none(email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    personnelToAdd = await Personnel.create(
        email=user.email,
        mot_de_passe=user.mdp,
        role=Role(user.role),  # Convertir la chaîne en enum
        nom=user.nom,
        telephone=user.telephone
    )
    return {"message": "Personnel enregistré", "id": clientToAdd.id}

@router.get("/")
async def getAllUser():
    personnel = await Personnel.all()
    return personnel 