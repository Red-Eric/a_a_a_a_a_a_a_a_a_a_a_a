from tortoise.models import Model
from tortoise import fields

class Favoris(Model):
    id = fields.IntField(pk = True)
    
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="favori",
        on_delete=fields.CASCADE
    )
    
    chambre = fields.ForeignKeyField(
        "models.Chambre",
        related_name="favori_chambre",
        on_delete=fields.CASCADE
    )
    
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="favori_etablissement",
        on_delete=fields.CASCADE
    );
    
    plat = fields.ForeignKeyField(
        "models.Plat",
        related_name="favori_plat",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "favoris"