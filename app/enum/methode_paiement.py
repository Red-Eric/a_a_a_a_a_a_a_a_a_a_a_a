from enum import Enum

# ('espèces', 'carte bancaire', 'mobile money', 'virement', 'autre') DEFAULT 'espèces',

class MethodePaiement(str, Enum):
    ESPECES = "Espèces"
    CARTE_CREDIT = "Carte de Crédit"
    MOBILE_MONEY = "Mobile Money"
    VIREMENT = "Virement"
    AUTRE = "Autre"
