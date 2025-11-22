from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str          # FIXED: was "username"
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
