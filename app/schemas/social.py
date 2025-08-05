from pydantic import BaseModel
from typing import Literal


class SocialLoginPayload(BaseModel):
    provider: Literal["google", "facebook"]
    token: str  # id_token pour Google, access_token pour Facebook
