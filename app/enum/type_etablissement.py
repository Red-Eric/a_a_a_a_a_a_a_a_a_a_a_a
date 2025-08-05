from enum import Enum

class Type_etablissement(str, Enum):
    HOTELERIE = "Hotelerie"
    RESTAURATION = "Restauration"
    HOTELERIE_RESTAURATION = "Hotelerie et Restauration"
