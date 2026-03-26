from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.deps import get_current_user, get_current_active_admin
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=schemas.MessageSchema)
def send_message(
    req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    # 1. Manage session
    if req.session_id:
        session = db.query(models.ChatSession).filter(
            models.ChatSession.id == req.session_id,
            models.ChatSession.user_id == user.id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        title = req.message[:30] + "..." if len(req.message) > 30 else req.message
        session = models.ChatSession(user_id=user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Save user message
    user_msg = models.ChatMessage(
        session_id=session.id,
        sender="user",
        content=req.message
    )
    db.add(user_msg)

    # 3. 🔥 REPLACE AI LOGIC (Render-safe)
    try:
        ai_response_text = f"You said: {req.message} (AI disabled for deployment)"
    except Exception:
        ai_response_text = "AI service temporarily unavailable."

    # 4. Save AI response
    ai_msg = models.ChatMessage(
        session_id=session.id,
        sender="ai",
        content=ai_response_text
    )
    db.add(ai_msg)

    db.commit()
    db.refresh(ai_msg)

    return ai_msg


@router.get("/sessions", response_model=List[schemas.ChatSessionSchema])
def get_user_sessions(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user.id
    ).all()


@router.get("/admin/all-sessions", response_model=List[schemas.ChatSessionSchema])
def get_all_sessions_admin(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_active_admin)
):
    return db.query(models.ChatSession).all()