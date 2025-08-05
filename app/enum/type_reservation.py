from enum import Enum


class TypeReservation(str, Enum):
    NORMAL = "Normal"
    GROUPE = "Groupe"
    LONG_SEJOUR = "Long séjour"