from pydantic import BaseModel, EmailStr
from app.enum.role import Role
from typing import Optional
from datetime import date
from app.enum.account_status import AccountStatus

class Personnel_Create(BaseModel):
    nom : str
    prenom : str
    telephone : str
    email : EmailStr
    mot_de_passe : Optional[str]
    etablissement_id : int
    role : Role
    poste : Optional[str] = ""
    date_embauche : date
    statut_compte : AccountStatus = AccountStatus.ACTIVE