from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from pydantic import BaseModel
from pydantic import EmailStr


engine = create_engine(
   'sqlite:///sqlite_db.db', connect_args={'check_same_thread': False})
# engine_conn = engine.connect()   

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
   


class User(Base):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, index=True)
   lname = Column(String)
   fname = Column(String)
   email = Column(String, unique=True, index=True)
   password = Column(String)
   todos = relationship("TODO", back_populates="owner", cascade="all, delete-orphan")
 
class TODO(Base):
   __tablename__ = "todos"
   id = Column(Integer, primary_key=True, index=True)
   text = Column(String, index=True)
   completed = Column(Boolean, default=False)
   owner_id = Column(Integer, ForeignKey("users.id"))
   owner = relationship("User", back_populates="todos")

Base.metadata.create_all(engine)