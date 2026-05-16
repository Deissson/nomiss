import json
import os
import time

import anthropic
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fallback for local development if DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./database.db"
elif DATABASE_URL.startswith("postgres://"):
    # SQLAlchemy requires postgresql:// instead of postgres://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SubjectModel(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    totalHours = Column(Integer)
    skipped = Column(Integer, default=0)
    last_skipped = Column(BigInteger, nullable=True)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database table creation failed: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nomiss-lyart.vercel.app"],
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

# Global Anthropic client cache for connection pooling
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_anthropic_client = None

def get_anthropic_client():
    global _anthropic_client
    if not _anthropic_client and ANTHROPIC_API_KEY:
        try:
            # Initialize lazily to prevent startup crashes and reduce initial memory footprint
            _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Failed to initialize Anthropic client: {e}")
    return _anthropic_client

class NewSubject(BaseModel):
    name: str
    totalHours: int

class ChatMessage(BaseModel):
    message: str
    file_base64: str | None = None
    file_type: str | None = None

@app.get("/")
def read_root():
    return {"status": "Backend is running with Postgres"}

@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(SubjectModel).all()

@app.post("/subjects")
def add_subject(subject: NewSubject, db: Session = Depends(get_db)):
    new_sub = SubjectModel(name=subject.name, totalHours=subject.totalHours)
    db.add(new_sub)
    db.commit()
    return db.query(SubjectModel).all()

@app.post("/skip/{subject_id}")
def skip_class(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    sub.skipped += 1
    sub.last_skipped = int(time.time())
    db.commit()
    return db.query(SubjectModel).all()

@app.post("/undo/{subject_id}")
def undo_skip(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    if sub.skipped > 0:
        sub.skipped -= 1
        sub.last_skipped = None
        db.commit()
    return db.query(SubjectModel).all()

@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if sub:
        db.delete(sub)
        db.commit()
    return db.query(SubjectModel).all()

@app.post("/chat")
def chat_with_tutor(chat: ChatMessage, db: Session = Depends(get_db)):
    # Optimize: Fetch only necessary columns to reduce database overhead
    subs = db.query(SubjectModel.name, SubjectModel.skipped).filter(SubjectModel.skipped > 0).all()
    missed_context = ", ".join(
        [f"{s.name} ({s.skipped} missed)" for s in subs]
    )

    system_prompt = (
        f"You are a concise, expert high school tutor. The student has missed these classes: {missed_context}. "
        "Analyze the provided materials (images or PDFs) and explain the core concepts. "
        "Focus on helping them catch up quickly. Be highly understandable and brief to save tokens. Avoid using Markdown in every instance (including other languages), structure the response strictly in plain text"
    )

    client = get_anthropic_client()
    if not client:
        return {
            "reply": f"[Demo Mode] Missed: {missed_context}. Question: {chat.message}. (Attach API Key for real AI)"
        }

    content = []

    if chat.file_base64 and chat.file_type:
        if "pdf" in chat.file_type:
            content.append({
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": chat.file_base64}
            })
        else:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": chat.file_type or "image/jpeg", "data": chat.file_base64}
            })

    content.append({
        "type": "text",
        "text": chat.message or "Explain this material based on my missed classes."
    })

    # Reuse global client to benefit from connection pooling and avoid re-initialization latency (~30ms)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )

    return {"reply": response.content[0].text}
