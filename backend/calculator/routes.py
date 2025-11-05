# backend/calculator/routes.py
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from datetime import datetime
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.calculator.footprint_cal import CarbonFootprintCalculator
from Database.mongo import carbon_collection

router = APIRouter(prefix="/calculator", tags=["Calculator"])

# Load Mongo URL from env if present
#MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
#MONGO_DBNAME = os.getenv("MONGO_DBNAME", "eco_app")

#mongo_client = MongoClient(MONGO_URL)
#mongo_db = mongo_client[MONGO_DBNAME]
#carbon_collection = mongo_db["carbon_footprints"]

# optional simple Pydantic model to validate incoming JSON is a dict
class PayloadModel(BaseModel):
    data: Optional[Dict[str, Any]] = None

@router.get("/test")
def test_route():
    return {"message": "Calculator routes working ✅"}

@router.post("/calculate")
def calculate_footprint(payload: Dict[str, Any],
                        Authorize: AuthJWT = Depends()):
    """
    Expects a JSON body (payload) with optional keys:
      - transportation: { inputs: {...} } OR transportation inputs directly
      - energy: { inputs: {...} } OR energy inputs directly
      - food: { inputs: {...} } OR food inputs directly
      - waste: { inputs: {...} } OR waste inputs directly

    Example payload is shown in the docs / examples below.
    Requires Authorization header: Bearer <access_token>
    """
    try:
        # verify token
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {e}")

    try:
        calculator = CarbonFootprintCalculator()
        results = calculator.calculate_from_payload(payload or {})
        # prepare record and insert into MongoDB
        record = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "results": results,
            "summary": results.get("summary", {})
        }
        carbon_collection.insert_one(record)

        return JSONResponse(status_code=201, content={
            "message": "Carbon footprint calculated and saved",
            "summary": results.get("summary", {}),
            "results": results
        })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/latest")
def get_latest_footprint(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {e}")

    try:
        latest = carbon_collection.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
        if not latest:
            raise HTTPException(status_code=404, detail="No results found for user")

        latest["_id"] = str(latest["_id"])
        latest["timestamp"] = latest["timestamp"].isoformat()
        return latest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))