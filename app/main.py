from fastapi import FastAPI
from app.routers import chatbot

app = FastAPI()

# Include routers
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI LangChain Project!"}
