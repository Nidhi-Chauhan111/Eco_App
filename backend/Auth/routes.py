#FastAPI routes for /signup and /login

# backend/Auth/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.Database.Journal import get_db
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
    return service.authenticate_user(db, request.email, request.password)
