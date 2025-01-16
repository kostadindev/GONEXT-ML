from fastapi import FastAPI
from app.routers import chatbot, tips

app = FastAPI()

# Include routers

app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(tips.router, prefix="/tips", tags=["Tips"])

# app.include_router(chatbot)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI LangChain Project!"}
