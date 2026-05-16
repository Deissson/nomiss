import os
import anthropic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SubjectModel
from ..schemas import ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
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

    client = anthropic.Anthropic(api_key=api_key)
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
