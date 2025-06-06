from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Request
from typing import List, Optional
import uvicorn
import random
import string
import httpx
from langchain_api import chat_stream
import requests
import sys
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
async def root():
    return {"message": "Hello World, pakistan zindabad"}

@app.get("/health")
async def health_check():
    TEST_MODEL_URL = os.getenv("TEST_MODEL_URL", "http://localhost:8000/v1/models")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(TEST_MODEL_URL)
            return {"status": "ok", "models": resp.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

  
@app.get("/random_string")
async def get_random_string(length: int = 10):
    """
    Generate a random string of fixed length
    """
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return {"random_string": letters}

@app.post("/get_prompt_response")
async def get_prompt_response(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    url = "http://127.0.0.1:11434/api/generate"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            url,
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            }
        )

    return response.json()

@app.post("/chat")
async def lang_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    print(f"Received prompt: {prompt}")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    return StreamingResponse(chat_stream(prompt), media_type="text/event-stream")

