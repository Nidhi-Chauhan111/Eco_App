 # business logic (hashing, validation, JWT)

 # backend/Auth/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.Auth import utils, models

def create_user(db: Session, username: str, email: str, password: str):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(password)
    new_user = models.User(username=username, email=email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not utils.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = utils.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
