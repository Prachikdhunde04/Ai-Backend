from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.deps import get_current_user, get_current_active_admin
from services.ai_service import query_rag
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=schemas.MessageSchema)
def send_message(req: schemas.ChatRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # 1. Provide logic to manage session
    if req.session_id:
        session = db.query(models.ChatSession).filter(models.ChatSession.id == req.session_id, models.ChatSession.user_id == user.id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        title = req.message[:30] + "..." if len(req.message) > 30 else req.message
        session = models.ChatSession(user_id=user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        
    # 2. Add user message to history
    user_msg = models.ChatMessage(session_id=session.id, sender="user", content=req.message)
    db.add(user_msg)
    
    # 3. Process via AI and RAG
    # This might take some time depending on local hardware
    try:
        ai_response_text = query_rag(req.message)
    except Exception as e:
        ai_response_text = "I encountered an error connecting to my local offline model. Make sure Ollama is running."
        # In a real app we might log the exception properly
    
    # 4. Add AI message to history
    ai_msg = models.ChatMessage(session_id=session.id, sender="ai", content=ai_response_text)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return ai_msg

@router.get("/sessions", response_model=List[schemas.ChatSessionSchema])
def get_user_sessions(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user.id).all()

@router.get("/admin/all-sessions", response_model=List[schemas.ChatSessionSchema])
def get_all_sessions_admin(db: Session = Depends(get_db), admin: models.User = Depends(get_current_active_admin)):
    # Admins can view all chats from all users
    return db.query(models.ChatSession).all()
