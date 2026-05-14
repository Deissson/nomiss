import json
import os
import threading
import time
from typing import List

import anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nomiss-lyart.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"

_db_cache: List[dict] | None = None
_db_last_mtime: float = 0
_db_lock = threading.Lock()


def load_db() -> List[dict]:
    global _db_cache, _db_last_mtime
    if not os.path.exists(DB_FILE):
        return []

    current_mtime = os.path.getmtime(DB_FILE)
    if _db_cache is not None and current_mtime <= _db_last_mtime:
        return _db_cache

    with _db_lock:
        # Double-check inside the lock
        current_mtime = os.path.getmtime(DB_FILE)
        if _db_cache is not None and current_mtime <= _db_last_mtime:
            return _db_cache

        with open(DB_FILE, "r") as f:
            _db_cache = json.load(f)
        _db_last_mtime = current_mtime
        return _db_cache


def save_db(data: List[dict]):
    global _db_cache, _db_last_mtime
    with _db_lock:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
        _db_cache = data
        _db_last_mtime = os.path.getmtime(DB_FILE)


class NewSubject(BaseModel):
    name: str
    totalHours: int


class ChatMessage(BaseModel):
    message: str
    file_base64: str | None = None
    file_type: str | None = None


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}


@app.get("/subjects")
def get_subjects():
    return load_db()


@app.post("/subjects")
def add_subject(subject: NewSubject):
    db = load_db()
    new_id = max([sub["id"] for sub in db], default=0) + 1
    db.append(
        {
            "id": new_id,
            "name": subject.name,
            "totalHours": subject.totalHours,
            "skipped": 0,
            "last_skipped": None,
        }
    )
    save_db(db)
    return db


@app.post("/skip/{subject_id}")
def skip_class(subject_id: int):
    db = load_db()
    for sub in db:
        if sub["id"] == subject_id:
            sub["skipped"] += 1
            sub["last_skipped"] = int(time.time())
            save_db(db)
            return db
    return db


@app.post("/undo/{subject_id}")
def undo_skip(subject_id: int):
    db = load_db()
    for sub in db:
        if sub["id"] == subject_id and sub["skipped"] > 0:
            sub["skipped"] -= 1
            sub["last_skipped"] = None
            save_db(db)
            return db
    return db


@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int):
    db = load_db()
    db = [sub for sub in db if sub["id"] != subject_id]
    save_db(db)
    return db


# --- TUTOR CHATBOT WITH PDF SUPPORT ---
@app.post("/chat")
def chat_with_tutor(chat: ChatMessage):
    db = load_db()
    missed_context = ", ".join(
        [f"{s['name']} ({s['skipped']} missed)" for s in db if s["skipped"] > 0]
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

    client = anthropic.Anthropic(api_key=api_key)
    content = []

    # Handle Attachments
    if chat.file_base64 and chat.file_type:
        if "pdf" in chat.file_type:
            # Send as PDF document
            content.append(
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": chat.file_base64,
                    },
                }
            )
        else:
            # Send as Image
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": chat.file_type
                        if chat.file_type
                        else "image/jpeg",
                        "data": chat.file_base64,
                    },
                }
            )

    content.append(
        {
            "type": "text",
            "text": chat.message or "Explain this material based on my missed classes.",
        }
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )

    return {"reply": response.content[0].text}  # pyright: ignore[reportAttributeAccessIssue]
