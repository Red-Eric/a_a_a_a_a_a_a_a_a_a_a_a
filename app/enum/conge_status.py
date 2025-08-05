from enum import Enum

class CongerStatus(str, Enum):
    EN_ATTENTE = "En Attente"
    APPROUVER = "Approuvé"
    REFUSER = "Refusé"
    ANNULER = "Annulé"
    
    