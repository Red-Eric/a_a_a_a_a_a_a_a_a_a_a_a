from fastapi import APIRouter, HTTPException,Body
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserLogin, TokenResponse, UserResponse, 
    RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm, 
    ChangePasswordRequest, SuperAdminResponse
)
from pydantic import EmailStr

from app.models.client import Client
from app.models.personnel import Personnel
from app.models.etablissement import Etablissement
from app.services.auth_service import AuthService
from app.schemas.etablissementCreate import EtablissementCreate
from app.schemas.personnel_create import Personnel_Create
from app.schemas.clientCreate import Client_Create
from app.services.email_service import send_email
from app.schemas.verify_code_create import VerifyCodeCreate
from app.models.verify_code import VerifyCode
from datetime import datetime, timedelta, timezone
import random

from app.config import config

router = APIRouter()

@router.post("/register/client", response_model=UserResponse)
async def register_client(data: Client_Create, code: str = Body(...)):
    """
    Enregistre un nouveau client et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.register_client(data, code)

@router.post("/register/etablissement", response_model=UserResponse)
async def register_etablissement(data: EtablissementCreate, code: str = Body(...)):
    """
    Enregistre un nouvel établissement et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.register_etablissement(data, code)

@router.post("/register/personnel", response_model=UserResponse)
async def register_personnel(data: Personnel_Create, code: str = Body(...)):
    """
    Enregistre un nouveau personnel et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.register_personnel(data, code)

@router.post("/login/client", response_model=TokenResponse)
async def login_client(data: UserLogin):
    """
    Authentifie un client et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.login_client(data)

@router.post("/login/etablissement", response_model=TokenResponse)
async def login_etablissement(data: UserLogin):
    """
    Authentifie un établissement et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.login_etablissement(data)

@router.post("/login/personnel", response_model=TokenResponse)
async def login_personnel(data: UserLogin):
    """
    Authentifie un personnel et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.login_personnel(data)

@router.post("/login/superadmin", response_model=TokenResponse)
async def login_superadmin(data: UserLogin):
    """
    Authentifie un superadmin et retourne un token d'accès et de rafraîchissement.
    """
    return await AuthService.login_superadmin(data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    """
    Rafraîchit un token d'accès à partir d'un token de rafraîchissement.
    """
    return await AuthService.refresh_token(data)


@router.post("/password/reset-request", response_model=dict)
async def request_password_reset(data: PasswordResetRequest):
    """
    Demande un lien de réinitialisation de mot de passe par email.
    """
    response = await AuthService.request_password_reset(data)
    reset_token = response["reset_token"]

    html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px;">
            <h2 style="color: #333333;">Réinitialisation de votre mot de passe</h2>
            <p>Bonjour,</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe. Veuillez utiliser le code de vérification ci-dessous pour continuer :</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; background-color: #e8f5e9; color: #2e7d32; font-size: 24px; padding: 15px 30px; border-radius: 8px; font-weight: bold;">
                {reset_token}
                </span>
            </div>
            <p><strong>Ce code expirera dans 5 minutes.</strong></p>
            <p>Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet e-mail.</p>
            <p>Merci,<br>L'équipe Support</p>
            <hr style="margin-top: 40px;">
            <p style="font-size: 12px; color: #777777;">Ceci est un message automatique, merci de ne pas y répondre.</p>
            </div>
        </body>
        </html>
    """

    await send_email(
        subject="Réinitialisation de mot de passe",
        to=data.email,
        body=html_content
    )

    return {"message": "Lien de réinitialisation envoyé par email"}




async def message_resetpassword(email, reset_token):
    html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px;">
            <h2 style="color: #333333;">Réinitialisation de votre mot de passe</h2>
            <p>Bonjour,</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe. Veuillez utiliser le code de vérification ci-dessous pour continuer :</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; background-color: #e8f5e9; color: #2e7d32; font-size: 24px; padding: 15px 30px; border-radius: 8px; font-weight: bold;">
                {reset_token}
                </span>
            </div>
            <p><strong>Ce code expirera dans 5 minutes.</strong></p>
            <p>Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet e-mail.</p>
            <p>Merci,<br>L'équipe Support</p>
            <hr style="margin-top: 40px;">
            <p style="font-size: 12px; color: #777777;">Ceci est un message automatique, merci de ne pas y répondre.</p>
            </div>
        </body>
        </html>
    """

    await send_email(
        subject="Réinitialisation de mot de passe",
        to=email,
        body=html_content
    )

@router.post("/password/client/reset-request", response_model=dict)
async def request_password_reset_client(data: PasswordResetRequest):
    """
    Demande un lien de réinitialisation de mot de passe par email.
    """
    response = await AuthService.request_password_reset_client(data)
    reset_token = response["reset_token"]

    await message_resetpassword(data.email, reset_token)

    return {"message": "Lien de réinitialisation envoyé par email"}


@router.post("/password/personnel/reset-request", response_model=dict)
async def request_password_reset_personnel(data: PasswordResetRequest):
    """
    Demande un lien de réinitialisation de mot de passe par email.
    """
    response = await AuthService.request_password_reset_personnel(data)
    reset_token = response["reset_token"]

    await message_resetpassword(data.email, reset_token)

    return {"message": "Lien de réinitialisation envoyé par email"}


@router.post("/password/etablissement/reset-request", response_model=dict)
async def request_password_reset_etablissement(data: PasswordResetRequest):
    """
    Demande un lien de réinitialisation de mot de passe par email.
    """
    response = await AuthService.request_password_reset_etablissement(data)
    reset_token = response["reset_token"]

    await message_resetpassword(data.email, reset_token)

    return {"message": "Lien de réinitialisation envoyé par email"}


@router.post("/password/superAdmin/reset-request", response_model=dict)
async def request_password_reset_superAdmin(data: PasswordResetRequest):
    """
    Demande un lien de réinitialisation de mot de passe par email.
    """
    response = await AuthService.request_password_reset_super_admin(data)
    reset_token = response["reset_token"]

    await message_resetpassword(data.email, reset_token)

    return {"message": "Lien de réinitialisation envoyé par email"}

#-----------------------------------------------------------------------------------
@router.post("/password/client/reset-confirm", response_model=dict)
async def reset_password_client(data: PasswordResetConfirm):
    """
    Réinitialise le mot de passe avec un token de réinitialisation.
    """
    return await AuthService.reset_password_client(data)

@router.post("/password/personnel/reset-confirm", response_model=dict)
async def reset_password_Personnel(data: PasswordResetConfirm):
    """
    Réinitialise le mot de passe avec un token de réinitialisation.
    """
    return await AuthService.reset_password_Personnel(data)

@router.post("/password/etablissement/reset-confirm", response_model=dict)
async def reset_password_Etablissement(data: PasswordResetConfirm):
    """
    Réinitialise le mot de passe avec un token de réinitialisation.
    """
    return await AuthService.reset_password_Etablissement(data)

@router.post("/password/superAdmin/reset-confirm", response_model=dict)
async def reset_password_SuperAdmin(data: PasswordResetConfirm):
    """
    Réinitialise le mot de passe avec un token de réinitialisation.
    """
    return await AuthService.reset_password_SuperAdmin(data)



@router.post("/password/change", response_model=dict)
async def change_password(data: ChangePasswordRequest, user_id: str, role: str):
    """
    Change le mot de passe de l'utilisateur authentifié.
    Note : user_id et role doivent être obtenus depuis le token JWT dans une implémentation réelle.
    """
    return await AuthService.change_password(user_id, role, data)


@router.post("/envoye-code")
async def create_verify_code(verify_code: VerifyCodeCreate):
    old_code = await VerifyCode.get_or_none(email=verify_code.email)
    if old_code:
        await old_code.delete()

    code = random.randint(100000, 999999)

    new_code = await VerifyCode.create(
        email=verify_code.email,
        code=code,
        expired_at=datetime.utcnow() + timedelta(minutes=5)
    )

    html_content = f"""
        <html>
            <body>
                <h2>Code de vérification pour l'inscription</h2>
                <p>Bonjour,</p>
                <p>Merci de vous être inscrit sur notre plateforme.</p>
                <p>Voici votre code de vérification pour finaliser votre inscription :</p>
                <h1 style="color: #4CAF50;">{new_code.code}</h1>
                <p>Ce code expirera dans 5 minutes.</p>
                <hr>
                <p style="font-size: 12px; color: #888;">Si vous n'avez pas initié cette inscription, veuillez ignorer ce message.</p>
            </body>
        </html>
    """


    await send_email(
        subject="Votre code de vérification",
        to=verify_code.email,
        body=html_content
    )

    return {
        "message": "Code de vérification envoyé avec succès.",
        "email": new_code.email
    }

@router.get("/current-user")
async def get_current_user_route(current=Depends(AuthService.get_current_user)):
    email = current["email"]
    role = current["role"]

    if role == "client":
        user = await Client.get_or_none(email=email)
    elif role == "etablissement":
        user = await Etablissement.get_or_none(email=email)
    elif role == "personnel":
        user = await Personnel.get_or_none(email=email)
    else:
        return {
            "message" : "Rôle personnel inconnu"
        }
    if not user:
        return {
            "message" : "Utilisateur Non trouver"
        }

    return user



@router.post("/verify-code")
async def verify_if_exist(
    email: EmailStr = Body(...),
    code: str = Body(...)
):
    verify_ = await VerifyCode.get_or_none(email=email, code=code)
    if not verify_:
        return {"message": "Code inexistant"}

    if verify_.expired_at < datetime.now(timezone.utc):
        return {"message": "Expiré"}

    return True