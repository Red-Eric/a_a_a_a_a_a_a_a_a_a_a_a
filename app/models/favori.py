from tortoise.models import Model
from tortoise import fields

class Favori(Model):
    id = fields.IntField(pk=True)

    client = fields.ForeignKeyField(
        "models.Client",
        related_name="favoris",  # ✅ nom unique ici
        on_delete=fields.CASCADE,
    )

    chambre = fields.ForeignKeyField(
        "models.Chambre",
        related_name="favoris_chambre",  # ✅ éviter le conflit
        on_delete=fields.CASCADE,
        null=True
    )

    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="favoris_etablissement",  # ✅ éviter le conflit
        on_delete=fields.CASCADE,
        null=True
    )

    plat = fields.ForeignKeyField(
        "models.Plat",
        related_name="favoris_plat",  # ✅ éviter le conflit
        on_delete=fields.CASCADE,
        null=True
    )

    class Meta:
        table = "favori"
        unique_together = [
            ("client", "chambre"),
            ("client", "etablissement"),
            ("client", "plat"),
        ]
