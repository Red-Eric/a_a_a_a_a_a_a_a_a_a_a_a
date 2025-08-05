from pydantic import BaseModel, EmailStr
from app.enum.role import Role
from typing import Optional
from datetime import date

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nom: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None

    class Config:
        orm_mode = True

class SuperAdminResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse | SuperAdminResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str