from tortoise.models import Model
from tortoise import fields
from app.enum.type_plat import Type_plat

class Plat(Model):
    id = fields.IntField(pk=True)
    libelle = fields.CharField(max_length=50)
    type = fields.CharEnumField(enum_type=Type_plat ,max_length=30)
    
    image_url = fields.CharField(
        max_length=255
    )
    description = fields.CharField(max_length=100, default="Plat moyenne btw")
    note = fields.IntField()
    prix = fields.IntField()
    
    disponible = fields.BooleanField()
    
    ingredients = fields.JSONField()
    tags = fields.JSONField()
    calories = fields.IntField()
    
    prep_minute =fields.IntField()
    
    

    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="plats",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "plat"
