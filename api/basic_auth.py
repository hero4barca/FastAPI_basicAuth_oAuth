from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from  . import models as models
from . import schemas as schemas
from .dependencies import get_db
from sqlalchemy.orm import  Session

security = HTTPBasic()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_user(db: Session, user_data: schemas.UserCreate) -> schemas.UserNormal:
    hashed_password = pwd_context.hash (user_data.password)
    db_user = models.User(
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


def get_current_user( db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security) ):
    valid_credentials = False
    user_from_db = db.query(models.User).filter(models.User.email == credentials.username).first()
    
    if not user_from_db == None:
        valid_credentials = pwd_context.verify(credentials.password, user_from_db.password )

    if not valid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user_from_db


def get_current_username( db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security) ):
    current_user = get_current_user(db, credentials)
    return current_user.email