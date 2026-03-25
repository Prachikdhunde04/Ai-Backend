from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, admin, documents, chat, reports
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Secure Offline AI Chatbot Backend", version="1.0")

# CORS setup
origins = [
    "http://localhost:3000",
    "https://v0-ai-chatbot-pia-gules.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "Secure AI Chatbot Backend is running."}