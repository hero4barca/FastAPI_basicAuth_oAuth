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
    


class TODOCreate(BaseModel):
   text: str
   completed: bool

class TODONormal(TODOCreate):
   id: int