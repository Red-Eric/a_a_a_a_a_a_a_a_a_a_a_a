from tortoise import fields
from tortoise.models import Model
from app.enum.methode_paiement import MethodePaiement
from app.enum.status_paiement import Status_Paiement

class Paiement_Plat(Model):
    id = fields.IntField(pk = True)
    date_de_paiement = fields.DatetimeField(auto_now_add=True)
    montant_total = fields.IntField()
    mode = fields.CharEnumField(enum_type=MethodePaiement, max_length=35)
    
    article = fields.JSONField()
    
    status = fields.CharEnumField(enum_type=Status_Paiement, max_length=35, default = Status_Paiement.EN_ATTENTE)
    
    caissier = fields.ForeignKeyField(
        "models.Personnel",
        related_name="paiement_plat",
        on_delete=fields.SET_NULL,
        null=True
    )
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="paiement_plat",
        on_delete=fields.CASCADE
    )
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="paiement_plat",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "paiement_plat"
    