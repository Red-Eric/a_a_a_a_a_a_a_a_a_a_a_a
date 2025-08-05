from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from app.enum.type_etablissement import Type_etablissement
from app.enum.etablissement_statu import Etablissement_status

class Etablissement(Model):
    id = fields.IntField(pk=True)
    nom = fields.CharField(max_length=100)
    adresse = fields.CharField(max_length=255)
    ville = fields.CharField(max_length=100)
    pays = fields.CharField(max_length=100)
    code_postal = fields.CharField(max_length=10, null=True)
    telephone = fields.CharField(max_length=20, null=True)
    email = fields.CharField(max_length=100, unique=True)
    site_web = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    
    type_ = fields.CharEnumField(
        enum_type=Type_etablissement,
        max_length=30,
        default = Etablissement_status.INACTIVE
    )  # Enum('hotel', 'restaurant', 'hotel and restaurant')

    mot_de_passe = fields.CharField(max_length=255)
    logo = fields.CharField(max_length=255, null=True)
    
    statut = fields.CharEnumField(
        enum_type=Etablissement_status,
        max_length=20,
        default=Etablissement_status.ACTIVE
    )  # Enum('active', 'inactive')
    
    reset_password_code = fields.CharField(max_length=255, null=True)
    reset_password_expires_at = fields.DatetimeField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    chambres: fields.ReverseRelation["Chambre"]

    class Meta:
        table = "etablissement"
