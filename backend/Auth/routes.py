#FastAPI routes for /signup and /login

# backend/Auth/routes.py
# backend/Auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Database.Journal import Base, SessionLocal
from Database.Journal import get_db
from backend.Auth import service
from backend.Auth.schemas import UserCreate, UserLogin  # ✅ import from schemas.py

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Route for signup
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    new_user = service.create_user(db, user.username, user.email, user.password)
    return {"message": "User created successfully", "user": new_user.email}

# ✅ Route for login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    token = service.authenticate_user(db, user.email, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}


'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from Database.Journal import get_db
from backend.Auth import service

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    new_user = service.create_user(db, user.username, user.email, user.password)
    return {"message": "User created successfully", "user": new_user.email}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return service.authenticate_user(db, request.email, request.password)'''
