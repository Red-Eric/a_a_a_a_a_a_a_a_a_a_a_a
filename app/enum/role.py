from enum import Enum

class Role(str, Enum):
    RECEPTIONNISTE = "Receptionniste"
    TECHNICIEN = "Technicien"
    MANAGER = "Manager"
    RH = "RH"
    CAISSIER = "Caissier"
    CLIENT =  "Client"
