from tortoise.models import Model
from tortoise import fields

class Notification(Model):
    id = fields.IntField(pk = True)
    
    message = fields.CharField(max_length=255)
    
    lu = fields.BooleanField()
    
    date = fields.DatetimeField(auto_now_add=True)
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="notification",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "notification"