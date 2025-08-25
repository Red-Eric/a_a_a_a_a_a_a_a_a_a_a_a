from tortoise.models import Model
from tortoise import fields
from app.enum.Notification import NotificationType, NotificationTitle


class Notification(Model):
    id = fields.IntField(pk = True)
    titre = fields.CharEnumField(enum_type=NotificationTitle , max_length=50)
    type = fields.CharEnumField(enum_type=NotificationType , max_length=50)
    
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