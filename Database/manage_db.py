# manage_db.py
import sys
import os

# Ensure project root is on sys.path (helps when running from different cwd)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import DB base & engine
from Database.db import Base, engine

# IMPORTANT: import all modules that declare models so they register with Base
# Adjust module import paths below if your project layout differs.
# These imports must execute class definitions that inherit Base.
import backend.Auth.models        # registers User
import Database.Journal           # registers UserStats, StreakEvent, Achievement

print("Dropping any existing tables known to Base (safe in dev)...")
Base.metadata.drop_all(bind=engine)

print("Creating tables from current models...")
Base.metadata.create_all(bind=engine)
print("Done — tables created. Current tables in metadata:", list(Base.metadata.tables.keys()))
