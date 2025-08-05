from tortoise.models import Model
from tortoise import fields
from app.enum.planing_event_status import PlanningEventStatus
from app.enum.planning_event_type import PlanningEventType

class PlanningEvent(Model):
    id = fields.IntField(pk = True)
    type = fields.CharEnumField(enum_type=PlanningEventType)
    status = fields.CharEnumField(enum_type=PlanningEventStatus)
    titre = fields.CharField(max_length = 25)
    description = fields.CharField(max_length = 50)
    
    dateDebut = fields.DatetimeField()
    dateFin = fields.DatetimeField()
    
    etablissement = fields.ForeignKeyField(
        "models.Etablissement",
        related_name="planning",
        on_delete=fields.CASCADE
    )
    
    personnel =fields.ForeignKeyField(
        "models.Personnel",
        related_name="planning_target",
        on_delete=fields.SET_NULL,
        null=True
    )
    
    responsable =fields.ForeignKeyField(
        "models.Personnel",
        related_name="planning_responsable",
        on_delete=fields.SET_NULL,
        null=True
    )
    
    
    
    class Meta:
        table = "planning_event"

    