from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from app.enum.status_reservation import Status_Reservation  
from app.enum.checking_type import CheckingType  
from app.enum.methode_paiement import MethodePaiement

class Reservation(Model):
    id = fields.IntField(pk=True, source_field="id_reservation")
    
    date_reservation = fields.DatetimeField(auto_now_add=True)
    date_arrivee = fields.DatetimeField()  
    date_depart = fields.DatetimeField()  
    duree = fields.IntField()
    
    articles = fields.JSONField(null = True)
    arhee = fields.JSONField(null = True)
    
    statut = fields.CharEnumField(
        enum_type=Status_Reservation,
        default=Status_Reservation.EN_ATTENTE,
        max_length=21
    )
    
    nbr_adultes = fields.IntField()
    nbr_enfants = fields.IntField()
    
    
    
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="reservations",
        source_field="client_id",
        on_delete=fields.CASCADE
    )
    
    chambre = fields.ForeignKeyField(
        "models.Chambre",
        related_name="reservations",
        source_field="chambre_id",
        null=True,
        on_delete=fields.CASCADE
    )
    
    
    mode_checkin = fields.CharEnumField(
        enum_type=CheckingType,
        default=CheckingType.MANUEL,
        max_length=20
    )
    
    code_checkin = fields.CharField(max_length=50, null=True)
    
    
    date_creation = fields.DatetimeField(auto_now_add=True)
    date_mise_a_jour = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reservation"
        table_description = "Réservations de chambres ou de tables par les clients"
        indexes = [
            ("client",),
        ]