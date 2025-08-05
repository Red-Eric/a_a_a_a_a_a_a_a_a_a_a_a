from pydantic import BaseModel, EmailStr
from typing import Optional
from app.enum.type_etablissement import Type_etablissement
from app.enum.etablissement_statu import Etablissement_status

class EtablissementCreate(BaseModel):
    nom: str
    adresse: str
    ville: str
    pays: str
    code_postal: Optional[str] = None
    telephone: Optional[str] = None
    email: EmailStr
    site_web: Optional[str] = None
    description: Optional[str] = None
    type_: Type_etablissement
    mot_de_passe: Optional[str]
    logo: Optional[str] = None
    statut: Etablissement_status = Etablissement_status.INACTIVE


class EtabStatus(BaseModel):
    statut : Etablissement_status
