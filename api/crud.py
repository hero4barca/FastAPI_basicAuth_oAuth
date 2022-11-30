from  . import models as models
from . import schemas as schemas
from sqlalchemy.orm import  Session
from fastapi import HTTPException

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