from fastapi import FastAPI
from app.routers import chatbot, tips, followups
from app.routers import game_overview

app = FastAPI()

# Include routers

app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(followups.router, prefix="/suggestions", tags=["Follow-ups"])
app.include_router(tips.router, prefix="/tips", tags=["Tips"])
app.include_router(game_overview.router, prefix="/game_overview", tags=["Game Overview"])

# app.include_router(chatbot)
@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI LangChain Project!"}
