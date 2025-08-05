from pydantic import BaseModel
from typing import Optional
from app.enum.status_table import status_table
from app.enum.type_table import Type_table

class Position(BaseModel):
    x : float
    y : float
    z : float
    
class Rotation(BaseModel):
    x : float
    y : float
    z : float

class Table_create(BaseModel):
    nom : str
    type : Type_table
    status : status_table
    position : Position
    rotation : Rotation
    client_id : int
    etablissement_id : int