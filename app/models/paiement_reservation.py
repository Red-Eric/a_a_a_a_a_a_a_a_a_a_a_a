from tortoise.models import Model
from tortoise import fields
from app.enum.methode_paiement import MethodePaiement
from app.enum.status_paiement import Status_Paiement

class Paiement_reservation(Model):
    id = fields.IntField(pk = True)
    date_de_paiement = fields.DatetimeField(auto_now_add=True)
    montant_total = fields.IntField()
    mode = fields.CharEnumField(enum_type=MethodePaiement, max_length=35)
    
    status = fields.CharEnumField(enum_type=Status_Paiement, max_length=35, default = Status_Paiement.EN_ATTENTE)
    
    article = fields.JSONField()
    
    caissier = fields.ForeignKeyField(
        "models.Personnel",
        related_name="paiement_reservation",
        on_delete=fields.SET_NULL,
        null=True
    )
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="paiement_reservation",
        on_delete=fields.CASCADE
    )
    
    reservation = fields.ForeignKeyField(
        "models.Reservation",
        related_name="paiement_reservation",
        on_delete=fields.CASCADE
    )
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="paiement_reservation",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "paiement_reservation"
    