from tortoise.models import Model
from tortoise import fields

class Incident(Model):
    id = fields.CharField(max_length = 255, pk= True)
    
    equipement = fields.ForeignKeyField(
        "models.Equipement",
        related_name="incident",
        on_delete=fields.CASCADE
    )
    
    title = fields.CharField(max_length = 255)
    
    description = fields.CharField(max_length = 255)
    
    severity = fields.CharField(max_length = 255)
    
    status = fields.CharField(max_length = 255)
    
    reportedAt = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
          table = "incident"
    