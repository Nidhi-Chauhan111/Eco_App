# backend/config.py

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT

# Load .env file from root
load_dotenv()

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY")

@AuthJWT.load_config
def get_config():
    return Settings()