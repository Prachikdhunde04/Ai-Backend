from fastapi import FastAPI
from database import engine, Base
import models
from routers import auth, admin, documents, chat, reports

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Offline AI Chatbot Backend", version="1.0")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"message": "Secure AI Chatbot Backend is running."}
