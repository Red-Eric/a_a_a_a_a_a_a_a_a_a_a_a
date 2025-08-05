from pydantic import BaseModel, EmailStr

class VerifyCodeCreate(BaseModel):
    email: EmailStr