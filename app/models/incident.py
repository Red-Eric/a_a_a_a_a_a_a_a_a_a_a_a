from tortoise.models import Model
from tortoise import fields

class Incident(Model):
    id = fields.CharField(max_length = 15, pk= True)
    
    nom = fields.CharField(max_length = 20)
    
    equipement = fields.ForeignKeyField(
        "models.Equipement",
        related_name="incident",
        on_delete=fields.CASCADE
    )
    
    title = fields.CharField(max_length = 20)
    
    description = fields.CharField(max_length = 50)
    
    severity = fields.CharField(max_length = 50)
    
    status = fields.CharField(max_length = 50)
    
    reportedAt = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
          table = "incident"
    