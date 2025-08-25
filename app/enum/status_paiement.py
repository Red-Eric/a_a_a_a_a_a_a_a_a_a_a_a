from enum import Enum

class Status_Paiement(str, Enum):
    REFUSER = "Refusé"
    EFFECTUER = "Effectué"
    EN_ATTENTE = "En Attente"
