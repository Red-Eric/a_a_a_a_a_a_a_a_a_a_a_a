from tortoise import fields
from tortoise.models import Model

class SuperAdmin(Model):
    id = fields.IntField(pk = True)
    email = fields.CharField(max_length = 255)
    password = fields.CharField(max_length = 255)
    reset_password_code = fields.CharField(max_length=255, null=True)
    reset_password_expires_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "super_admin" 