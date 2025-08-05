from enum import Enum

class Status_rapport(str, Enum):
    EN_ATTENTE = "En Attente"
    TRAITER = "Traiter"
    CLOTURER = "Clôturé"
