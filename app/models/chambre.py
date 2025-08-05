from tortoise.models import Model
from tortoise import fields
from app.enum.room_type import TypeChambre
from app.enum.etat_chambre import EtatChambre
from datetime import datetime

class Chambre(Model):
    id = fields.IntField(pk=True)
    numero = fields.CharField(max_length=10)
    
    capacite = fields.IntField()
    
    equipements = fields.JSONField()
    
    categorie = fields.CharEnumField(
        enum_type=TypeChambre,
        max_length=50
    )
    description = fields.TextField(null=True)
    tarif = fields.DecimalField(max_digits=10, decimal_places=2)
    photo_url = fields.CharField(max_length=255, null=True, default = "https://www.hotelarrizulcongress.com/wp-content/uploads/sites/51/2016/11/arrizul_hotel_congress_gallery_suite_01.jpg")
    
    etat = fields.CharEnumField(
        enum_type=EtatChambre,
        max_length=20,
        default=EtatChambre.LIBRE
    )

    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="chambres",
        on_delete=fields.CASCADE
    )

    date_creation = fields.DatetimeField(auto_now_add=True)
    date_mise_a_jour = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "chambre"
