from tortoise import fields
from tortoise.models import Model
from datetime import datetime, date
from app.models.etablissement import Etablissement
from app.enum.role import Role 
from app.enum.account_status import AccountStatus

class Personnel(Model):
    id = fields.IntField(pk=True)
    
    nom = fields.CharField(max_length=50)
    prenom = fields.CharField(max_length=50)
    telephone = fields.CharField(max_length=20, null=True)

    email = fields.CharField(max_length=100, unique=True)
    mot_de_passe = fields.CharField(max_length=255)

    salaire = fields.IntField(default = 100000)

    role = fields.CharEnumField(
        enum_type=Role,
        max_length=30
    )

    poste = fields.CharField(max_length=50, null=True)
    date_embauche = fields.DateField(null=True)

    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="personnels",
        on_delete=fields.CASCADE,
        source_field="etablissement_id"
    )

    statut_compte = fields.CharEnumField(
        enum_type=AccountStatus,
        max_length=20,
        default=AccountStatus.ACTIVE
    )

    reset_password_code = fields.CharField(max_length=255, null=True)
    reset_password_expires_at = fields.DatetimeField(null=True)

    date_creation = fields.DatetimeField(auto_now_add=True)
    date_mise_a_jour = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "personnel"
        table_description = "Table du personnel affecté à un établissement"
        indexes = [
            ("etablissement",),
            ("email",),
        ]
