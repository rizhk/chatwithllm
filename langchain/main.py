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
    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            url = "http://localhost:8000/v1/models"
            print(f"Trying to connect to LLM server at {url}")
            resp = await client.get(url)
            
            print(f"Response status: {resp.status_code}")
            print(f"Response text: {resp.text[:500]}...")  # First 500 chars
            
            try:
                return {"status": "healthy", "code": resp.status_code, "data": resp.json()}
            except Exception as je:
                return {"status": "healthy", "code": resp.status_code, "raw_response": resp.text[:500], "json_error": str(je)}
                
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

  
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

