from tortoise.models import Model
from tortoise import fields
from app.enum.methode_paiement import MethodePaiement

class Arhee(Model):
    id = fields.IntField(pk = True)
    montant = fields.IntField()
    date_paiement = fields.DatetimeField()
    mode_paiement = fields.CharEnumField(enum_type=MethodePaiement, max_length = 50)
    commentaire = fields.CharField(max_length = 50)
    
    