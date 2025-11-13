from backend.Journal.main import db_manager
from backend.Auth.models import User
from Database.Journal import UserStats, StreakEvent, Achievement
from datetime import date

# Get DB session
session = db_manager.get_postgres_session()

# STEP 1 — Create a user
new_user = User(username="Nakul", email="nakul@example.com", password="nak26")
session.add(new_user)
session.commit()
session.refresh(new_user)
print(f"✅ Created user: {new_user.username}, id={new_user.id}")

# Use new_user.id (integer)
user_stats = UserStats(user_id=new_user.id, username=new_user.username)
session.add(user_stats)
session.commit()

# STEP 2 — Create related records
stats = UserStats(user_id=new_user.id, username="Nakul", current_streak=5, total_entries=3)
event = StreakEvent(user_id=new_user.id, event_type="continued", streak_count=5)
achievement = Achievement(user_id=new_user.id, achievement_type="first_entry", achievement_name="First Step")

session.add_all([stats, event, achievement])
session.commit()

print("✅ Added stats, event, and achievement.")

# STEP 3 — Query relationships
user = session.query(User).filter_by(email="nidhi@example.com").first()
print("\n🧭 Relationship Checks:")
print("Stats:", user.stats)
print("Events:", user.streak_events)
print("Achievements:", user.achievements)

# STEP 4 — Reverse check
stat = session.query(UserStats).first()
print("\n🔁 This stat belongs to user:", stat.user.username)
