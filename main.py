from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, admin, documents, chat, reports
import os  # For getting Render's PORT

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Secure Offline AI Chatbot Backend", version="1.0")

# CORS setup - allow your frontend URL(s)
origins = [
    "http://localhost:3000",  # if testing locally
    "https://v0-ai-chatbot-pia-gules.vercel.app/",  # replace with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(reports.router)

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "Secure AI Chatbot Backend is running."}

# Run Uvicorn using Render's PORT environment variable
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # default to 8000 locally
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)