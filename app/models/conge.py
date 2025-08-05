from tortoise.models import Model
from tortoise import fields
from app.enum.conge_status import CongerStatus
from app.enum.conge_type import CongerTypee

class Conge(Model):
    id = fields.IntField(pk = True)
    type = fields.CharEnumField(enum_type=CongerTypee)
    status = fields.CharEnumField(enum_type=CongerStatus)
    
    dateDebut = fields.DatetimeField()  
    dateDmd = fields.DatetimeField()
    
    dateFin = fields.DatetimeField()
    raison = fields.CharField(max_length = 50)
    
    fichierJoin = fields.CharField(max_length = 255)
    

    
    personnel = fields.ForeignKeyField(
        "models.Personnel",
        related_name="conger",
        on_delete=fields.CASCADE
    )
    
    
    class Meta:
        table = "conge"

    