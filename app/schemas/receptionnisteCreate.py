from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.enum.role import Role
from app.enum.account_status import AccountStatus

class ReceptionnisteCreate(BaseModel):
    nom: str
    prenom: str
    telephone: Optional[str] = None
    email: EmailStr
    mot_de_passe: str
    role: Role
    poste: Optional[str] = None
    date_embauche: Optional[date] = None
    etablissement_id: int
    statut_compte: AccountStatus = AccountStatus.ACTIVE
    reset_password_token: Optional[str] = None
    reset_password_expires_at: Optional[datetime] = None
