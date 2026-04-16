import json
import os
import time
from typing import List

import anthropic
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

IS_PRODUCTION = os.environ.get("PRODUCTION") == "true"
DB_COOKIE_NAME = "subjects_db"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"


def load_db(request: Request | None = None) -> List[dict]:
    if IS_PRODUCTION and request:
        db_cookie = request.cookies.get(DB_COOKIE_NAME)
        if db_cookie:
            try:
                return json.loads(db_cookie)
            except json.JSONDecodeError:
                return []
        return []
    else:
        if not os.path.exists(DB_FILE):
            return []
        with open(DB_FILE, "r") as f:
            return json.load(f)


def save_db(data: List[dict], response: Response | None = None):
    if IS_PRODUCTION and response:
        response.set_cookie(
            key=DB_COOKIE_NAME, value=json.dumps(data), httponly=True, samesite="lax"
        )
    else:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)


class NewSubject(BaseModel):
    name: str
    totalHours: int


class ChatMessage(BaseModel):
    message: str
    file_base64: str | None = None
    file_type: str | None = None


# --- API Endpoints ---
@app.get("/subjects")
def get_subjects(request: Request, response: Response):
    db = load_db(request)
    save_db(db, response)  # Ensure cookie is set/updated even on GET requests
    return db


@app.post("/subjects")
def add_subject(subject: NewSubject, request: Request, response: Response):
    db = load_db(request)
    new_id = max([sub["id"] for sub in db], default=0) + 1
    # Initialize last_skipped as None
    db.append(
        {
            "id": new_id,
            "name": subject.name,
            "totalHours": subject.totalHours,
            "skipped": 0,
            "last_skipped": None,
        }
    )
    save_db(db, response)
    return {"message": "Subject added"}


@app.post("/skip/{subject_id}")
def skip_class(subject_id: int, request: Request, response: Response):
    db = load_db(request)
    for sub in db:
        if sub["id"] == subject_id:
            sub["skipped"] += 1
            sub["last_skipped"] = int(time.time())
            save_db(db, response)
            return {"message": "Skip recorded"}
    return {"error": "Not found"}


@app.post("/undo/{subject_id}")
def undo_skip(subject_id: int, request: Request, response: Response):
    db = load_db(request)
    for sub in db:
        if sub["id"] == subject_id and sub["skipped"] > 0:
            sub["skipped"] -= 1
            # Optional: Clear timestamp if no skips left
            sub["last_skipped"] = None
            save_db(db, response)
            return {"message": "Skip removed"}
    return {"error": "Not found"}


@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, request: Request, response: Response):
    db = load_db(request)
    db = [sub for sub in db if sub["id"] != subject_id]
    save_db(db, response)
    return {"message": "Subject deleted"}


# --- TUTOR CHATBOT WITH PDF SUPPORT ---
@app.post("/chat")
def chat_with_tutor(chat: ChatMessage, request: Request):
    db = load_db(request)
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
