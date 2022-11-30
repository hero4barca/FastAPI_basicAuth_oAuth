from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
import json, os, secrets
from  . import models as schemas
from .dependencies import get_db
from sqlalchemy.orm import  Session


from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional, List
from passlib.context import CryptContext

app = FastAPI()

security = HTTPBasic()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# def get_current_user(db: Session = Depends(get_db),
#                 	token: str = Depends(oauth2_scheme)):
#    return decode_access_token(db, token)

# @app.get("/api/me", response_model=schemas.User)
# def read_logged_in_user(current_user: schemas.User = Depends(get_current_user)):
#    """return user settings for current user"""
#    return current_user

def get_all_users(db: Session) -> List[schemas.User]:
    return db.query(schemas.User).filter().all()

def get_user_by_email(db: Session, email: str) -> Optional[schemas.User]:
    return db.query(schemas.User).filter(schemas.User.email == email).first()



def create_user(db: Session, user_data: schemas.UserCreate) -> schemas.UserNormal:
    hashed_password = pwd_context.hash (user_data.password)
    db_user = schemas.User(
        email=user_data.email,
        lname=user_data.lname,
        fname=user_data.fname,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    signedup_user = schemas.UserNormal(lname= db_user.lname, fname=db_user.fname, email=db_user.email)  
    return signedup_user


def get_current_username( db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security) ):
    valid_credentials = False
    user_from_db = db.query(schemas.User).filter(schemas.User.email == credentials.username).first()
    
    if not user_from_db == None:
        valid_credentials = pwd_context.verify(credentials.password, user_from_db.password )
 
    # print(user_from_db)
    #current_username_bytes = credentials.username.encode("utf8")

    # correct_username_bytes = b"stanleyjobson"

    # is_correct_username = secrets.compare_digest(
    #     current_username_bytes, correct_username_bytes
    # )
    # current_password_bytes = credentials.password.encode("utf8")
    # correct_password_bytes = b"swordfish"

    # is_correct_password = secrets.compare_digest(
    #     current_password_bytes, correct_password_bytes
    # )
    #if not (is_correct_username and is_correct_password):

    if not valid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/users/all")
async def all_users(db: Session = Depends(get_db)):
    all_users_list = get_all_users(db)
    return all_users_list



@app.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


@app.post("/api/users", response_model=schemas.UserNormal)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
   """add new user"""
   user = get_user_by_email(db, user_data.email)
   if user:
    raise HTTPException(status_code=409,
   	                    detail="Email already registered.")
   signedup_user = create_user(db, user_data)
   return signedup_user


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/index")
async def index():
    car = {"model": "corolla 2019",
            "brand": "toyota",
            "price": 2000000}

    return car 
