# backend/calculator/routes.py
import os
from fastapi import APIRouter, HTTPException, Depends, Body
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

         # generate recommendations using the same logic as CLI
        rec_obj = calculator.generate_recommendations_from_results(results)

        # prepare record and insert into MongoDB
        record = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "results": results,
            "summary": results.get("summary", {}),
            "recommendations": rec_obj
        }
        inserted = carbon_collection.insert_one(record)
        record_id = str(inserted.inserted_id)

        response_payload = {
            "message": "Carbon footprint calculated and saved",
            "record_id": record_id,
            "summary": results.get("summary", {}),
            "results": results,
            "recommendations": rec_obj
        }
        return JSONResponse(status_code=201, content=response_payload)
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


@router.post("/recommendations")
def get_recommendations(payload: Dict[str, Any], Authorize: AuthJWT = Depends()):

    # 1. Auth
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {e}")

    # 2. Load calculator
    calc = CarbonFootprintCalculator()

    # 3. Extract inputs
    transport_inputs = payload.get("transportation", {})
    energy_inputs = payload.get("energy", {})
    food_inputs = payload.get("food", {})
    waste_inputs = payload.get("waste", {})

    # 4. Calculate emissions (needed for recommendations)
    t_em = calc.transport_calc.calculate_emissions(transport_inputs)
    e_em = calc.energy_calc.calculate_emissions(energy_inputs)
    f_em = calc.food_calc.calculate_emissions(food_inputs)
    w_em = calc.waste_calc.calculate_emissions(waste_inputs)

    # 5. Collect recommendations
    recs = []
    recs += calc.transport_calc.get_recommendations(t_em, transport_inputs)
    recs += calc.energy_calc.get_recommendations(e_em, energy_inputs)
    recs += calc.food_calc.get_recommendations(f_em, food_inputs)
    recs += calc.waste_calc.get_recommendations(w_em, waste_inputs)

    return {
        "success": True,
        "user_id": user_id,
        "recommendations": {
            "count": len(recs),
            "recommendations": recs,
        }
    }