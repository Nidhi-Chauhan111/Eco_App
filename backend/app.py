# FastAPI launcher 
# backend/app.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.Auth import routes as auth_routes

app = FastAPI(title="Eco_App Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allow frontend access during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth routes
app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to Eco-App Backend!"}


#run using: uvicorn backend.app:app --reload
