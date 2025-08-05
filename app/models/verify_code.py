from tortoise import fields
from tortoise.models import Model

class VerifyCode(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    code = fields.IntField(null=False)
    expired_at = fields.DatetimeField(null=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "verify_code"
