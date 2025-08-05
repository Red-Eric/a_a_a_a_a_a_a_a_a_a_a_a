from tortoise.models import Model
from tortoise import fields

class Avis(Model):
    id = fields.IntField(pk = True)
    comment = fields.TextField()
    note = fields.IntField()
    date_creation = fields.DatetimeField(auto_now_add=True)
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="avis",
        on_delete=fields.CASCADE
    )
    
    chambre = fields.ForeignKeyField(
        "models.Chambre",
        related_name="avis",
        on_delete=fields.CASCADE,
        null=True
    )
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="avis_etablissement",
        on_delete=fields.CASCADE,
        null=True
    )
    
    plat = fields.ForeignKeyField(
        "models.Plat",
        related_name="avis_plat",
        on_delete=fields.CASCADE,
        null=True
    )
    
    class Meta:
        table = "avis"