from enum import Enum

class NotificationTitle(str, Enum):
    AJOUT = "Ajout"
    SUPPRESSION = "Suppression"
    MODIFICATION = "Modification"
    PATCH = "Patch"
    CONFIRMATION = "Confirmation"

class NotificationType(str, Enum):
    CHAMBRE = "Chambre"
    RESERVATION = "Reservation"
    COMMANDE = "Commande"
    PLAT = "Plat"
    PERSONNEL = "Personnel"
