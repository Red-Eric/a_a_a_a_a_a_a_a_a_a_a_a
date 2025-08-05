from enum import Enum


class MethodePaiement(str, Enum):
    ESPECES = "Espèces"
    CARTE_CREDIT = "Carte de Crédit"
    MOBILE_MONEY = "Mobile Money"
    VIREMENT = "Virement"
    AUTRE = "autre"