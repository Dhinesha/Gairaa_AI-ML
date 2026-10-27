import os
from datetime import timedelta
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)

load_dotenv()
app = FastAPI(
    title="FastAPI + LangChain + Gemini",
    description="A MINI friendly chatbot API powered by Google Gemini — with JWT Authentication.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    response: str

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY is missing. Add it to your .env file.",
        )
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
    )

@app.get("/", tags=["Health"])
def root():
    return {"status": "API is running ✅", "version": "2.0.0"}

@app.post("/register", tags=["Auth"], summary="Register a new user")
def register(body: RegisterRequest):
    if not body.username.strip() or not body.password.strip():
        raise HTTPException(status_code=400, detail="Username and password cannot be empty.")
    create_user(body.username.strip(), body.password)
    return {"detail": f"User '{body.username}' registered successfully. You can now login."}

@app.post("/login", response_model=TokenResponse, tags=["Auth"], summary="Login and get a JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"], summary="Chat with Gemini (requires login)")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    llm = get_llm()
    ai_message = llm.invoke(request.message)
    content = ai_message.content

    if isinstance(content, list):
        response_text = " ".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    else:
        response_text = content

    return ChatResponse(
        message=request.message,
        response=response_text,
    )
