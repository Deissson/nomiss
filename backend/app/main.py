import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import SubjectModel
from .routes import subjects, chat

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NoMiss API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nomiss-lyart.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Migration logic: JSON to Postgres
DB_FILE = "database.json"
def migrate_json_to_postgres():
    db = SessionLocal()
    try:
        if db.query(SubjectModel).count() == 0 and os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    new_sub = SubjectModel(
                        name=item["name"],
                        totalHours=item["totalHours"],
                        skipped=item.get("skipped", 0),
                        last_skipped=item.get("last_skipped")
                    )
                    db.add(new_sub)
                db.commit()
                print("Migration from JSON to Postgres completed.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        db.close()

migrate_json_to_postgres()

app.include_router(subjects.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"status": "Backend is running with Postgres", "version": "2.0.0"}
