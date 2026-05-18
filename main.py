import json
import os
import time
import threading
import logging
from contextlib import asynccontextmanager

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
    # Ensure SSL is used for Render Postgres
    if "sslmode" not in DATABASE_URL:
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require"

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
        migrate_json_to_postgres()
    except Exception as e:
        logging.error(f"Startup database initialization failed: {e}")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nomiss-lyart.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client cache for optimization
_anthropic_client = None
_anthropic_lock = threading.Lock()

def get_anthropic_client():
    """
    Returns a thread-safe singleton instance of the Anthropic client.
    This optimization avoids the ~32ms overhead of re-instantiating the client
    on every request and enables connection pooling.
    """
    global _anthropic_client
    if _anthropic_client is None:
        with _anthropic_lock:
            if _anthropic_client is None:
                api_key = os.environ.get("ANTHROPIC_API_KEY", "")
                _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client

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
    subs = db.query(SubjectModel).filter(SubjectModel.skipped > 0).all()
    missed_context = ", ".join(
        [f"{s.name} ({s.skipped} missed)" for s in subs]
    )

    system_prompt = (
        f"You are a concise, expert high school tutor. The student has missed these classes: {missed_context}. "
        "Analyze the provided materials (images or PDFs) and explain the core concepts. "
        "Focus on helping them catch up quickly. Be highly understandable and brief to save tokens. Avoid using Markdown in every instance (including other languages), structure the response strictly in plain text"
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {
            "reply": f"[Demo Mode] Missed: {missed_context}. Question: {chat.message}. (Attach API Key for real AI)"
        }

    client = get_anthropic_client()
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

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )

    return {"reply": response.content[0].text}
