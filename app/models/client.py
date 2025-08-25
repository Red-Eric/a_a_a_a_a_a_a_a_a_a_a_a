from tortoise import fields
from tortoise.models import Model
from datetime import date
from app.enum.account_status import AccountStatus
from app.models.chambre import Chambre
from app.models.reservation import Reservation
from app.enum.status_reservation import Status_Reservation
from app.enum.checking_type import CheckingType  # Assure-toi qu’il existe
from app.enum.sexe import Sexe


class Client(Model):
    id = fields.IntField(pk=True, source_field="client_id")
    last_name = fields.CharField(max_length=50)
    first_name = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=20, null=True)
    email = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=255, null=True)
    pays = fields.CharField(max_length=60, null=True)
    sexe = fields.CharEnumField(enum_type=Sexe, max_length=35)
    
    
    # preferences = fields.TextField(null=True)

    account_status = fields.CharEnumField(
        enum_type=AccountStatus,
        default=AccountStatus.ACTIVE
    )

    reset_password_code = fields.CharField(max_length=255, null=True)
    reset_password_expires_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    reservations: fields.ReverseRelation["Reservation"]
    

    async def reserver_chambre(self, chambre_id: int, date_debut: date, date_fin: date):
        chambre = await Chambre.get_or_none(id=chambre_id)
        if not chambre:
            return {"message": "Chambre inexistante"}

        duree = (date_fin - date_debut).days
        if duree <= 0:
            return {"message": "Dates invalides"}

        reservation = await Reservation.create(
            date_arrivee=date_debut,
            date_depart=date_fin,
            duree=duree,
            statut=Status_Reservation.EN_ATTENTE,
            nb_personnes=1,
            client=self,
            chambre=chambre,
            # plus de etablissement ici
            mode_checkin=CheckingType.MANUEL
        )

        return {"message": "Réservation enregistrée", "reservation_id": reservation.id}

    class Meta:
        table = "client"
        indexes = [
            ("email",)
        ]
        table_description = "Clients associated with an establishment"
