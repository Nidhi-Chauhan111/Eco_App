# FastAPI launcher 
# backend/app.py
# backend/app.py



from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
import auth_config

# import routes
from backend.Auth import routes as auth_routes
from backend.calculator import routes as calculator_routes  #importing calculator route
from backend.Journal import routes as journal_routes #importing journal routes


app = FastAPI(title="Eco_App Backend")

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:3000","http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for fastapi_jwt_auth exceptions
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc: AuthJWTException):
    # Use exc.message (human friendly) — str(exc) can be empty for these exceptions.
    msg = getattr(exc, "message", None) or getattr(exc, "detail", None) or str(exc) or "Invalid authentication header"
    return JSONResponse(status_code=getattr(exc, "status_code", 422), content={"detail": msg})

# include routers
app.include_router(auth_routes.router)
app.include_router(calculator_routes.router)  #  register calculator API
app.include_router(journal_routes.router) #register journal backend API

@app.get("/")
def root():
    return {"message": "Welcome to Eco-App Backend!"}



#run using: uvicorn backend.app:app --reload
