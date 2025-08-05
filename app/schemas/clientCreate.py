from pydantic import BaseModel, EmailStr
from typing import Optional
from app.enum.account_status import AccountStatus
from app.enum.sexe import Sexe

class Client_Create(BaseModel):
    first_name: str
    last_name: str
    sexe : Sexe = Sexe.HOMME
    phone: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    pays: Optional[str] = None
    # preferences: Optional[str] = None
    account_status: AccountStatus = AccountStatus.ACTIVE
