# import requests

# response = requests.post(
#     "http://localhost:11434/api/chat",
#     json={
#         "model": "gemma:2b",
#         "messages": [{"role": "user", "content": "Hello"}]
#     }
# )

# print(response.status_code)
# print(response.text)

import litellm
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

# Tell litellm where to find the ollama server
# litellm.api_base = "http://localhost:11434"

# Call ollama/llama3
# response = litellm.completion(
#   model="ollama/gemma:2b",
#   messages=[{"role": "user", "content": "Hello from Litellm + Ollama!"}],
#   api_base="http://localhost:11434"
# )

# print(response.choices[0].message.content)

from langchain_openai import ChatOpenAI

# Point to your local LiteLLM proxy
async def chat_stream(message: str):
    MODEL_LISTENING_URL = os.getenv("MODEL_LISTENING_URL")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt2")
    
    chat = ChatOpenAI(
        openai_api_base= f"{MODEL_LISTENING_URL}",  # LiteLLM proxy URL
        model=MODEL_NAME,
        openai_api_key="EMPTY"
    )

    # Stream response token by token
    for chunk in chat.stream(message):
        print(chunk.content)
        yield chunk.content  # Yield only the content string
