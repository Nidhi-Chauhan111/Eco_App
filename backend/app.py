# FastAPI launcher 
# backend/app.py
# backend/app.py



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import routes
from backend.Auth import routes as auth_routes
from backend.calculator import routes as calculator_routes  #importing calculator route
import config

app = FastAPI(title="Eco_App Backend")

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_routes.router)
app.include_router(calculator_routes.router)  #  register calculator API

@app.get("/")
def root():
    return {"message": "Welcome to Eco-App Backend!"}



#run using: uvicorn backend.app:app --reload
