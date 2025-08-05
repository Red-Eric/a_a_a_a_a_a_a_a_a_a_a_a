from tortoise import fields
from tortoise.models import Model
from app.enum.status_table import status_table
from app.enum.type_table import Type_table



class Table(Model):
    id = fields.IntField(pk=True)
    nom = fields.CharField(max_length = 30, default = "Table sans_nom")
    status = fields.CharEnumField(enum_type=status_table, max_length=25, default = status_table.LIBRE)
    type= fields.CharEnumField(enum_type=Type_table, max_length=35)
    
    positionX = fields.FloatField()
    positionY = fields.FloatField()
    positionZ = fields.FloatField()
    
    rotationX = fields.FloatField()
    rotationY = fields.FloatField()
    rotationZ = fields.FloatField()
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="Table",
        on_delete=fields.CASCADE
    )
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="Table",
        on_delete=fields.SET_NULL,
        null=True
    )
    
    class Meta:
        table = "table"