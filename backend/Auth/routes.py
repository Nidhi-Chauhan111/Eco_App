#FastAPI routes for /signup and /login

# backend/Auth/routes.py
# backend/Auth/routes.py
from config import Settings
from fastapi_jwt_auth import AuthJWT

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
def login(user: UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    db_user = service.verify_user_credentials(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = Authorize.create_access_token(subject=str(db_user.id))
    return {"access_token": access_token, "token_type": "bearer"}



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
