from enum import Enum

class Status_Paiement(str, Enum):
    REFUSER = "Refuser"
    EFFECTUER = "Effectuer"
    EN_ATTENTE = "En Attente"
