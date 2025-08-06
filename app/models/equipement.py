from tortoise.models import Model
from tortoise import fields

class Equipement(Model):
    id = fields.CharField(max_length = 15, pk = True)
    nom = fields.CharField(max_length = 20)
    type = fields.CharField(max_length = 20)
    localisation = fields.CharField(max_length = 20)
    status = fields.CharField(max_length = 20)
    description = fields.CharField(max_length = 50)
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="equipement",
        on_delete=fields.CASCADE
    )
    
    
    class Meta:
          table = "equipement"
    