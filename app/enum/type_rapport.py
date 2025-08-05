from enum import Enum

class TypeRapport(str, Enum):
    INCIDENT = "Incident"
    MAINTENANCE = "Maintenance"
    NETTOYAGE = "Nettoyage"
    RESTAURATION = "Restauration"
    RESSOURCES_HUMAINES = "Ressources Humaines"
    AUTRE = "Autre"
