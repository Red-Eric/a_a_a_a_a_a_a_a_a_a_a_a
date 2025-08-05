from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from app.models.etablissement import Etablissement
from app.models.client import Client
from app.models.personnel import Personnel
from app.models.superAdmin import SuperAdmin
from app.schemas.etablissementCreate import EtablissementCreate
from app.schemas.clientCreate import Client_Create
from app.schemas.personnel_create import Personnel_Create
from app.schemas.auth import RefreshTokenRequest, UserLogin, UserResponse, ChangePasswordRequest, PasswordResetConfirm, PasswordResetRequest, SuperAdminResponse, TokenResponse
from app.enum.account_status import AccountStatus
from app.enum.etablissement_statu import Etablissement_status
import os
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from app.models.verify_code import VerifyCode
import random

load_dotenv()

# Configuration JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_HOURS = 1
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SUPERADMIN_EMAIL = "admin@ghr.com"
SUPERADMIN_PASSWORD = "$2b$12$J8iUHpdRMYsyREUpemB45OD0oVxvUh.F9A0ABxkQCIwI9pbvdE4oG"

class AuthService:
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Type de token invalide"
                )
                
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            if user_id is None or email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
            return {"user_id": user_id, "email": email, "role": payload.get("role")}
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash un mot de passe"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Crée un token de rafraîchissement JWT"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Type de token invalide"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

    @staticmethod
    async def register_etablissement(user_data: EtablissementCreate, code: str) -> UserResponse:
        """Enregistrement d'un nouvel établissement"""
        if await Etablissement.get_or_none(email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        verify = await VerifyCode.get_or_none(email=user_data.email, code=code)
        if not verify:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification invalide"
            )

        if verify.expired_at < datetime.now(timezone.utc):
            await verify.delete()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification expiré"
            )

        etablissement = await Etablissement.create(
            nom=user_data.nom,
            adresse=user_data.adresse,
            ville=user_data.ville,
            pays=user_data.pays,
            code_postal=user_data.code_postal,
            telephone=user_data.telephone,
            email=user_data.email,
            site_web=user_data.site_web,
            description=user_data.description,
            type_=user_data.type_,
            mot_de_passe=AuthService.get_password_hash(user_data.mot_de_passe),
            statut=user_data.statut,
            logo=user_data.logo
        )

        token_data = {
            "sub": str(etablissement.id),
            "email": etablissement.email,
            "role": "etablissement"
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        
        await verify.delete()
        
        return UserResponse(
            id=etablissement.id,
            email=etablissement.email,
            nom=etablissement.nom,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def register_client(user_data: Client_Create, code:str) -> UserResponse:
        """Enregistrement d'un nouveau client"""
        if await Client.get_or_none(email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        verify = await VerifyCode.get_or_none(email=user_data.email, code=code)
        if not verify:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification invalide"
            )

      

        if verify.expired_at < datetime.now(timezone.utc):
            await verify.delete()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification expiré"
            )


        client = await Client.create(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=AuthService.get_password_hash(user_data.password),
            phone=user_data.phone,
            pays=user_data.pays,
            preferences=user_data.preferences,
            account_status=user_data.account_status
        )

        token_data = {
            "sub": str(client.id),
            "email": client.email,
            "role": "client"
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        await verify.delete()
        
        return UserResponse(
            id=client.id,
            email=client.email,
            first_name=client.first_name,
            last_name=client.last_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def register_personnel(user_data: Personnel_Create, code: str) -> UserResponse:
        """Enregistrement d'un nouveau personnel"""
        if await Personnel.get_or_none(email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        verify = await VerifyCode.get_or_none(email=user_data.email, code=code)
        if not verify:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification invalide"
            )

        if verify.expired_at < datetime.now(timezone.utc):
            await verify.delete()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code de vérification expiré"
            )
        
        etablissement = await Etablissement.get_or_none(id=user_data.etablissement_id)
        if not etablissement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Établissement non trouvé"
            )

        personnel = await Personnel.create(
            nom=user_data.nom,
            prenom=user_data.prenom,
            telephone=user_data.telephone,
            email=user_data.email,
            mot_de_passe=AuthService.get_password_hash(user_data.mot_de_passe),
            role=user_data.role,
            poste=user_data.poste,
            date_embauche=user_data.date_embauche,
            etablissement=etablissement,
            statut_compte=user_data.statut_compte
        )

        token_data = {
            "sub": str(personnel.id),
            "email": personnel.email,
            "role": "personnel",
            "etablissement_id": personnel.etablissement_id
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        await verify.delete()
        
        return UserResponse(
            id=personnel.id,
            email=personnel.email,
            first_name=personnel.prenom,
            last_name=personnel.nom,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def login_etablissement(credentials: UserLogin) -> TokenResponse:
        """Login pour les établissements"""
        etablissement = await Etablissement.get_or_none(email=credentials.email)
        if not etablissement or not AuthService.verify_password(credentials.password, etablissement.mot_de_passe):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if etablissement.statut != Etablissement_status.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte établissement inactif"
            )

        token_data = {
            "sub": str(etablissement.id),
            "email": etablissement.email,
            "role": "etablissement"
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            user=UserResponse(
                id=etablissement.id,
                email=etablissement.email,
                nom=etablissement.nom
            )
        )

    @staticmethod
    async def login_personnel(credentials: UserLogin) -> TokenResponse:
        """Login pour le personnel"""
        personnel = await Personnel.get_or_none(email=credentials.email)
        if not personnel or not AuthService.verify_password(credentials.password, personnel.mot_de_passe):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if personnel.statut_compte != AccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte personnel inactif"
            )

        token_data = {
            "sub": str(personnel.id),
            "email": personnel.email,
            "role": "personnel",
            "etablissement_id": personnel.etablissement_id
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            user=UserResponse(
                id=personnel.id,
                email=personnel.email,
                first_name=personnel.prenom,
                last_name=personnel.nom
            )
        )

    @staticmethod
    async def login_client(credentials: UserLogin) -> TokenResponse:
        """Login pour les clients"""
        client = await Client.get_or_none(email=credentials.email)
        if not client or not AuthService.verify_password(credentials.password, client.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if client.account_status != AccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte client inactif"
            )

        token_data = {
            "sub": str(client.id),
            "email": client.email,
            "role": "client"
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            user=UserResponse(
                id=client.id,
                email=client.email,
                first_name=client.first_name,
                last_name=client.last_name
            )
        )

    @staticmethod
    async def login_superadmin(credentials: UserLogin) -> TokenResponse:
        """Login pour super admin"""
        if credentials.email != SUPERADMIN_EMAIL or not AuthService.verify_password(credentials.password, SUPERADMIN_PASSWORD):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )

        superadmin = await SuperAdmin.get_or_none(email=credentials.email)
        if not superadmin:
            superadmin = await SuperAdmin.create(
                email=SUPERADMIN_EMAIL,
                password=SUPERADMIN_PASSWORD
            )

        token_data = {
            "sub": str(superadmin.id),
            "email": superadmin.email,
            "role": "superadmin"
        }
        
        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            user=SuperAdminResponse(
                id=superadmin.id,
                email=superadmin.email
            )
        )

    @staticmethod
    async def refresh_token(refresh_request: RefreshTokenRequest) -> TokenResponse:
        """Rafraîchit un token d'accès à partir d'un token de rafraîchissement"""
        payload = AuthService.verify_token(refresh_request.refresh_token, "refresh")
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        etablissement_id = payload.get("etablissement_id")

        if not user_id or not email or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de rafraîchissement invalide"
            )

        token_data = {
            "sub": user_id,
            "email": email,
            "role": role
        }
        if etablissement_id:
            token_data["etablissement_id"] = etablissement_id

        access_token = AuthService.create_access_token(token_data)
        new_refresh_token = AuthService.create_refresh_token(token_data)

        user_response = None
        if role == "etablissement":
            etablissement = await Etablissement.get_or_none(id=user_id)
            if etablissement:
                user_response = UserResponse(id=etablissement.id, email=etablissement.email, nom=etablissement.nom)
        elif role == "client":
            client = await Client.get_or_none(id=user_id)
            if client:
                user_response = UserResponse(id=client.id, email=client.email, first_name=client.first_name, last_name=client.last_name)
        elif role == "superadmin":
            superadmin = await SuperAdmin.get_or_none(id=user_id)
            if superadmin:
                user_response = SuperAdminResponse(id=superadmin.id, email=superadmin.email)
        else:  # personnel
            personnel = await Personnel.get_or_none(id=user_id)
            if personnel:
                user_response = UserResponse(id=personnel.id, email=personnel.email, first_name=personnel.prenom, last_name=personnel.nom)

        if not user_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            user=user_response
        )

    @staticmethod
    async def request_password_reset_client(request: PasswordResetRequest) -> dict:
        """Génère un token de réinitialisation de mot de passe"""
        user = None
        role = None
        user = await Client.get_or_none(email=request.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun utilisateur trouvé avec cet email"
            )

        reset_token =  random.randint(100000, 999999)
        expires_at = datetime.now() + timedelta(minutes=5)

        user.reset_password_code = reset_token
        user.reset_password_expires_at = expires_at
        await user.save()

        return {"message": "Lien de réinitialisation envoyé", "reset_token": reset_token}
    

    @staticmethod
    async def request_password_reset_etablissement(request: PasswordResetRequest) -> dict:
        """Génère un token de réinitialisation de mot de passe"""
        user = None
        role = None
        user = await Etablissement.get_or_none(email=request.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun utilisateur trouvé avec cet email"
            )

        reset_token =  random.randint(100000, 999999)
        expires_at = datetime.now() + timedelta(minutes=5)

        user.reset_password_code = reset_token
        user.reset_password_expires_at = expires_at
        await user.save()

        return {"message": "Lien de réinitialisation envoyé", "reset_token": reset_token}
    

    @staticmethod
    async def request_password_reset_personnel(request: PasswordResetRequest) -> dict:
        """Génère un token de réinitialisation de mot de passe"""
        user = None
        role = None
        user = await Personnel.get_or_none(email=request.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun utilisateur trouvé avec cet email"
            )

        reset_token =  random.randint(100000, 999999)
        expires_at = datetime.now() + timedelta(minutes=5)

        user.reset_password_code = reset_token
        user.reset_password_expires_at = expires_at
        await user.save()

        return {"message": "Lien de réinitialisation envoyé", "reset_token": reset_token}
    
    
    
    @staticmethod
    async def request_password_reset_super_admin(request: PasswordResetRequest) -> dict:
        """Génère un token de réinitialisation de mot de passe"""
        user = None
        role = None
        user = await SuperAdmin.get_or_none(email=request.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun utilisateur trouvé avec cet email"
            )

        reset_token =  random.randint(100000, 999999)
        expires_at = datetime.now() + timedelta(minutes=5)

        user.reset_password_code = reset_token
        user.reset_password_expires_at = expires_at
        await user.save()

        return {"message": "Lien de réinitialisation envoyé", "reset_token": reset_token}


    @staticmethod
    async def reset_password_client(confirm: PasswordResetConfirm) -> dict:
        """Réinitialise le mot de passe avec le token fourni"""
        user = None
        role = None
        user = await Client.get_or_none(reset_password_code=confirm.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide"
            )

        if user.reset_password_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation expiré"
            )


        hashed_password = AuthService.get_password_hash(confirm.new_password)
        user.password = hashed_password
        user.reset_password_code = None
        user.reset_password_expires_at = None
        await user.save()

        return {"message": "Mot de passe réinitialisé avec succès"}
    
    @staticmethod
    async def reset_password_Etablissement(confirm: PasswordResetConfirm) -> dict:
        """Réinitialise le mot de passe avec le token fourni"""
        user = None
        role = None
        user = await Etablissement.get_or_none(reset_password_code=confirm.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide"
            )

        if user.reset_password_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation expiré"
            )


        hashed_password = AuthService.get_password_hash(confirm.new_password)
        user.mot_de_passe = hashed_password
        user.reset_password_code = None
        user.reset_password_expires_at = None
        await user.save()

        return {"message": "Mot de passe réinitialisé avec succès"}
    
    @staticmethod
    async def reset_password_Personnel(confirm: PasswordResetConfirm) -> dict:
        """Réinitialise le mot de passe avec le token fourni"""
        user = None
        role = None
        user = await Personnel.get_or_none(reset_password_code=confirm.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide"
            )

        if user.reset_password_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation expiré"
            )


        hashed_password = AuthService.get_password_hash(confirm.new_password)
        user.mot_de_passe = hashed_password
        user.reset_password_code = None
        user.reset_password_expires_at = None
        await user.save()

        return {"message": "Mot de passe réinitialisé avec succès"}
    
    @staticmethod
    async def reset_password_SuperAdmin(confirm: PasswordResetConfirm) -> dict:
        """Réinitialise le mot de passe avec le token fourni"""
        user = None
        role = None
        user = await SuperAdmin.get_or_none(reset_password_code=confirm.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide"
            )

        if user.reset_password_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation expiré"
            )


        hashed_password = AuthService.get_password_hash(confirm.new_password)
        user.password = hashed_password
        user.reset_password_code = None
        user.reset_password_expires_at = None
        await user.save()

        return {"message": "Mot de passe réinitialisé avec succès"}

    @staticmethod
    async def change_password(user_id: str, role: str, request: ChangePasswordRequest) -> dict:
        """Change le mot de passe de l'utilisateur authentifié"""
        user = None
        if role == "client":
            user = await Client.get_or_none(id=user_id)
        elif role == "personnel":
            user = await Personnel.get_or_none(id=user_id)
        elif role == "etablissement":
            user = await Etablissement.get_or_none(id=user_id)
        elif role == "superadmin":
            user = await SuperAdmin.get_or_none(id=user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        password_field = "password" if role in ["client", "superadmin"] else "mot_de_passe"
        if not AuthService.verify_password(request.current_password, getattr(user, password_field)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )

        hashed_password = AuthService.get_password_hash(request.new_password)
        setattr(user, password_field, hashed_password)
        await user.save()

        return {"message": "Mot de passe changé avec succès"}

        