import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models
from routers import auth, admin, documents, chat, reports

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Secure AI Chatbot Backend",
    version="1.0"
)

# ✅ CORS (allow all for deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # IMPORTANT for frontend connection
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(reports.router)

# Root endpoint (test)
@app.get("/")
def read_root():
    return {"message": "Secure AI Chatbot Backend is running 🚀"}

# Health check (optional but useful)
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Render-compatible run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render gives PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)