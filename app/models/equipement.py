from tortoise.models import Model
from tortoise import fields

class Equipement(Model):
    id = fields.CharField(max_length = 255, pk = True)
    nom = fields.CharField(max_length = 255)
    type = fields.CharField(max_length = 255)
    localisation = fields.CharField(max_length = 255)
    status = fields.CharField(max_length = 255)
    description = fields.CharField(max_length = 255)
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="equipement",
        on_delete=fields.CASCADE
    )
    
    
    class Meta:
          table = "equipement"
    