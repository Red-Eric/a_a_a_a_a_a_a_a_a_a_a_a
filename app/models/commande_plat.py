from tortoise.models import Model
from tortoise import fields

class Commande_Plat(Model):
    id = fields.IntField(pk = True)
    montant = fields.IntField()
    quantite = fields.IntField()
    description = fields.CharField(max_length = 255, null = True)
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="commande_plat",
        source_field="client_id",
        on_delete=fields.CASCADE
    )
    
    
    plat = fields.ForeignKeyField(
        "models.Plat",
        related_name="commande_plat",
        source_field="plat_id",
        null=True,
        on_delete=fields.SET_NULL
    )
    
    class Meta:
        table = "commande_plat"