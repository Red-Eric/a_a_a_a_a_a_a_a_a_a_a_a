from tortoise import fields
from tortoise.models import Model

class Intervention(Model):
    id = fields.IntField(pk = True)
    date = fields.DatetimeField(auto_now_add=True)
    
    personnel = fields.ForeignKeyField(
        "models.Personnel",
        related_name="intervention_personnel",
        on_delete=fields.CASCADE
    )
    
    equipement = fields.ForeignKeyField(
        "models.Equipement",
        related_name="equipement_personnel",
        on_delete=fields.CASCADE
    )
    
    description = fields.CharField(max_length = 255)
    status = fields.CharField(max_length = 255)
 
    class Meta:
        table = "intervention"   
    