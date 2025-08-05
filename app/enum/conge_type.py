from enum import Enum

class CongerTypee(str, Enum):
    VACANCE = "Vacance"
    MALADIE = "Maladie"
    RTT = "RTT"
    PARENTALE = "Congé parentale"
    FORMATION = "Formation"
    AUTRE = "Autre"
    
    