from pydantic import BaseModel

class User_Create(BaseModel):
    email: str
    mdp: str
    role: str
    access: str
    telephone: str
    nom: str