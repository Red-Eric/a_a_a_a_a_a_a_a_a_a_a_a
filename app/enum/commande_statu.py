from enum import Enum

# type de commande , mitovy amn ihan

class CommandeStatu(str, Enum):
    EN_ATTENTE = "En attente"
    CONFIRMEE = "Confirmée"
    ANNULEE = "Annulée"

