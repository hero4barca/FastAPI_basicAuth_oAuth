from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
import json, os, secrets
from  . import models as models
from . import schemas as schemas
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

def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).filter().all()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

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

def create_todo(db: Session, current_user: models.User, todo_data: schemas.TODOCreate):
   todo = models.TODO(text=todo_data.text,
                   	completed=todo_data.completed)
   todo.owner = current_user
   db.add(todo)
   db.commit()
   db.refresh(todo)
   return todo

def update_todo(db: Session, id: int, current_user: models.User, todo_data: schemas.TODOCreate):
   todo = db.query(models.TODO).filter(models.TODO.id == id).first()

   if todo == None:
    raise HTTPException(status_code=404,
   	                    detail="object not found")

   if not todo.owner  == current_user:
    raise HTTPException(status_code=401, detail="permission denied: operation not allowed")

   todo.text = todo_data.text
   todo.completed = todo_data.completed
   db.commit()
   db.refresh(todo)
   return todo

def delete_todo(db: Session, current_user: models.User,  id: int):
   todo = db.query(models.TODO).filter(models.TODO.id == id).first()

   if todo == None:
    raise HTTPException(status_code=404,
   	                    detail="object not found")
   if not todo.owner  == current_user:
    raise HTTPException(status_code=401, detail="permission denied: operation not allowed")                    
   
   db.delete(todo)
   db.commit()

def get_user_todos(db: Session, userid: int):
   return db.query(models.TODO).filter(models.TODO.owner_id == userid).all()


@app.get("/api/mytodos", response_model=List[schemas.TODONormal])
async def get_own_todos(current_user: models.User = Depends(get_current_user),
             	db: Session = Depends(get_db)):
   """return a list of TODOs owned by current user"""
   todos = get_user_todos(db, current_user.id)

   todo_list = []
   for todo in todos:
    todo_list.append(schemas.TODONormal(id=todo.id, text=todo.text, completed=todo.completed)) 
   
   return todo_list

@app.post("/api/todos", response_model=schemas.TODONormal)
async def add_a_todo(todo_data: schemas.TODOCreate,
          	current_user: models.User = Depends(get_current_user),
          	db: Session = Depends(get_db)):
   """add a TODO"""
   todo = create_todo(db, current_user, todo_data)
   return schemas.TODONormal(id=todo.id, text=todo.text, completed=todo.completed)

@app.put("/api/todos/{todo_id}", response_model=schemas.TODONormal)
async def update_a_todo(todo_id: int,
             	todo_data: schemas.TODOCreate,
             	current_user: models.User = Depends(get_current_user),
             	db: Session = Depends(get_db)):
   """update and return TODO for given id"""
#    todo = get_todo(db, todo_id)
   updated_todo = update_todo(db, todo_id, current_user, todo_data)
   return schemas.TODONormal(id=updated_todo.id, text=updated_todo.text, completed=updated_todo.completed ) 

@app.delete("/api/todos/{todo_id}")
async def delete_a_todo(todo_id: int,
             	current_user: models.User = Depends(get_current_user),
             	db: Session = Depends(get_db)):
   """delete TODO of given id"""
   delete_todo(db, current_user, todo_id)
   return {"detail": "TODO Deleted"}


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
async def api_root():
    return "Todo api root"
