from pydantic import BaseModel

class NotificationCreate(BaseModel):
    message : str
    lu : bool
    etablissement_id : int
    