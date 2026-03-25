from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.deps import get_current_active_admin, get_current_user
from services.ai_service import add_document_to_rag, summarize_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import io

router = APIRouter(prefix="/documents", tags=["Documents"])

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

@router.post("/upload/company")
async def upload_company_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_active_admin)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for now.")
    
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    chunks = text_splitter.split_text(text)
    metadatas = [{"source": file.filename} for _ in chunks]
    
    add_document_to_rag(chunks, metadatas)
    
    doc_record = models.DocumentRecord(filename=file.filename, uploaded_by=admin.id, is_company_wide=True)
    db.add(doc_record)
    db.commit()
    
    return {"message": f"Successfully processed and embedded {file.filename} into RAG."}

@router.post("/upload/summarize")
async def upload_for_summary(
    file: UploadFile = File(...),
    user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for now.")
    
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    # Truncate context if it's vastly too huge for a local LLM prompt
    if len(text) > 10000:
        text = text[:10000] 
        
    summary = summarize_text(text)
    return {"summary": summary, "filename": file.filename}
