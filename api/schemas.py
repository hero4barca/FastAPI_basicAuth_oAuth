from pydantic import BaseModel
from pydantic import EmailStr

class UserBase(BaseModel):
   email: EmailStr

class UserCreate(UserBase):
   lname: str
   fname: str
   password: str

class UserNormal(BaseModel):
   lname: str
   fname: str
   email: EmailStr

class UserOauth(BaseModel):
    hashed_password: str 
    username: EmailStr 
    lname: str
    fname: str 

class TODOCreate(BaseModel):
   text: str
   completed: bool

class TODONormal(TODOCreate):
   id: int

# Tokens for oauth authetiction
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

