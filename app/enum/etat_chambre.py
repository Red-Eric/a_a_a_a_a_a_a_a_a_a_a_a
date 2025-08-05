from enum import Enum

#occuper libre n, en net , hors ser

class EtatChambre(str, Enum):
    OCCUPEE = "Occupée"
    HORSSERVICE = "Hors Service"
    LIBRE = "Libre"
    NETTOYAGE = "En Nettoyage"
    
