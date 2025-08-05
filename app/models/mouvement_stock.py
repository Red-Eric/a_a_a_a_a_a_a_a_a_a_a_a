from tortoise import fields
from tortoise.models import Model
from app.enum.type_mouvement_stock import Type_mouvement_stock


class MouvementStock(Model):
    id = fields.IntField(pk = True)
    
    produit = fields.ForeignKeyField(
        "models.Produit",
        related_name="mouvement_stock_produit",
        on_delete= fields.CASCADE
    )
    
    personnel = fields.ForeignKeyField(
        "models.Personnel",
        related_name="mouvement_stock_personnel",
        on_delete= fields.CASCADE
    )
    
    
    quantite = fields.BigIntField()
    type = fields.CharEnumField(enum_type=Type_mouvement_stock)
    raison = fields.TextField()
    
    class Meta:
        table = "mouvement_stock"