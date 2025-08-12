from enum import Enum

# type de commande , mitovy amn ihan

class CommandeStatu(str, Enum):
    # EN_ATTENTE = "En attente"
    # CONFIRMEE = "Confirmée"
    # ANNULEE = "Annulée"
    ENCOURS = "Encours"
    ACCEPTE = "Acceptée"
    LIVREE = "Livrée"
    REFUSEE = "Réfusée"
    PAYEE = "Payée"

