import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "eco_app")

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DBNAME]
carbon_collection = mongo_db["carbon_footprints"]

def ensure_indexes():
    """Ensure MongoDB indexes for optimized queries"""
    carbon_collection.create_index("user_id")
    carbon_collection.create_index("timestamp")