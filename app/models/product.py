from tortoise import fields
from tortoise.models import Model

class Produit(Model):
    id = fields.IntField(pk = True)
    nom = fields.CharField(max_length = 35, unique=True)
    quantite = fields.BigIntField()
    prix = fields.BigIntField()
    
    seuil_stock = fields.IntField()
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="produits",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "produits"
    