from enum import Enum

class Status_Reservation(str, Enum):
    EN_ATTENTE = "En Attente"
    REFUSER = "REFUSER"
    CONFIRMER = "Confirmer"
    TERMINER = "Terminer"
    ANNULER = "Annuler"
