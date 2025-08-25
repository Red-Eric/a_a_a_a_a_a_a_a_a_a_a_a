from enum import Enum

class Status_Reservation(str, Enum):
    EN_ATTENTE = "En Attente"
    REFUSER = "Refusé"
    CONFIRMER = "Confirmé"
    TERMINER = "Terminé"
    ANNULER = "Annulé"


