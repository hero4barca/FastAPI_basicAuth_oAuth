from sqlalchemy.orm import  Session
from .models import SessionLocal, User
from fastapi import Depends


def get_db() -> Session:
    try:
        db = SessionLocal()
        yield db

    finally:
        db.close()


# def get_current_user(db: Session = Depends(get_db),
#                 	token: str = Depends(oauth2_scheme)):
#    return decode_access_token(db, token)


# @app.get("/api/me", response_model=User)
# def read_logged_in_user(current_user: User = Depends(get_current_user)):
#    """return user settings for current user"""
#    return current_user