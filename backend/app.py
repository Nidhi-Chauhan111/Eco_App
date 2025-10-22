# FastAPI launcher 
# backend/app.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from backend.Auth import routes as auth_routes

app = FastAPI(title="Eco_App Backend")

# Include Auth routes
app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to Eco-App Backend!"}


#run using: uvicorn backend.app:app --reload
