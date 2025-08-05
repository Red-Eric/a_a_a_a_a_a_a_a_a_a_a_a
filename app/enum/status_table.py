from enum import Enum

class status_table(str, Enum):
    LIBRE = "Libre"
    OCCUPE = "Occupée"
    RESERVEE = "Reservé"
    NETTOYAGE = "Nettoyage"
    HORS_SERVICE = "Hors-service"