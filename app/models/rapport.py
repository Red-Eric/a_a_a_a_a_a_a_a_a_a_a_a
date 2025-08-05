from tortoise.models import Model
from tortoise import fields
from app.enum.type_rapport import TypeRapport
from app.enum.status_rapport import Status_rapport

class Rapport(Model):
    id = fields.IntField(pk=True)

    # Dates
    date = fields.DatetimeField(auto_now_add=True)  # Date du rapport
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Liens
    personnel = fields.ForeignKeyField(
        "models.Personnel",
        related_name="rapports",
        null=True,
        on_delete=fields.SET_NULL
    )


    type = fields.CharEnumField(enum_type=TypeRapport , max_length=25)
    titre = fields.CharField(max_length=255, null=True)
    
    description = fields.TextField(null=True)
    reponse_responsable = fields.TextField(null=True, default = "")
    
    statut = fields.CharEnumField(enum_type=Status_rapport , max_length=30, default = Status_rapport.EN_ATTENTE)

    class Meta:
        table = "rapport"
