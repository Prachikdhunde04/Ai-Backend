import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, admin, documents, chat, reports

# Create DB tables
Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(
    title="Secure Offline AI Chatbot Backend",
    version="1.0"
)

# CORS
origins = [
    "http://localhost:8000",
    "https://v0-ai-chatbot-pia-gules.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now (safe to test)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(reports.router)

# Test route
@app.get("/")
def read_root():
    return {"message": "Backend is LIVE 🚀"}

# IMPORTANT: Render-compatible run
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render gives PORT
    uvicorn.run(app, host="0.0.0.0", port=port)