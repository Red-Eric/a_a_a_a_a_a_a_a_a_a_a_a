from enum import Enum

class PlanningEventStatus(str, Enum):
    CONFIRME = "Confirmée"
    EN_ATTENTE = "En Attente"
    ANNULER = "Annulée"
    TERMINER = "Terminée"
