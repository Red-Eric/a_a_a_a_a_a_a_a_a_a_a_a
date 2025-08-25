from fastapi import APIRouter, HTTPException, status
from app.schemas.social import SocialLoginPayload
from app.schemas.auth import TokenResponse, UserResponse
from app.models.client import Client
from app.enum.account_status import AccountStatus
from app.services.auth_service import AuthService
import httpx

router = APIRouter()


@router.post("/social-login", response_model=TokenResponse)
async def social_login(data: SocialLoginPayload):
    email = ""
    first_name = ""
    last_name = ""

    if data.provider == "google":
        # Vérifier l'id_token via l'API Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={data.token}"
            )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Token Google invalide")
        user_data = response.json()
        email = user_data.get("email")
        first_name = user_data.get("given_name", "")
        last_name = user_data.get("family_name", "")

    elif data.provider == "facebook":
        # Vérifier access_token via l'API Facebook
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?fields=id,email,first_name,last_name&access_token={data.token}"
            )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Token Facebook invalide")
        user_data = response.json()
        email = user_data.get("email")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")

    else:
        raise HTTPException(status_code=400, detail="Provider non supporté")

    if not email:
        raise HTTPException(status_code=400, detail="Email non récupéré depuis le provider")

    # Vérifier si le client existe déjà
    client = await Client.get_or_none(email=email)

    if not client:
        # Créer un nouveau client
        client = await Client.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="",  # Pas de mot de passe car auth externe
            phone=None,
            pays=None,
            preferences=None,
            sexe = "Autre",
            account_status=AccountStatus.ACTIVE
        )

    if client.account_status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Compte inactif")

    # Génération des tokens
    token_data = {
        "sub": str(client.id),
        "email": client.email,
        "role": "client"
    }

    access_token = AuthService.create_access_token(token_data, isMobile=True)
    refresh_token = AuthService.create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 60,
        user=UserResponse(
            id=client.id,
            email=client.email,
            first_name=client.first_name,
            last_name=client.last_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    )
