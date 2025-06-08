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

from langchain_community.llms import HuggingFaceEndpoint

# Point to your local LiteLLM proxy
async def chat_stream(message: str):
    HF_TOKEN = os.getenv("HF_TOKEN")
    REPO_ID = os.getenv("REPO_ID")
    

    llm = HuggingFaceEndpoint(
        repo_id=REPO_ID,
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        max_new_tokens=100,
        streaming=True
    )
    

    # Stream response token by token
    for chunk in llm.stream(message):
        print(chunk.content)
        yield chunk.content  # Yield only the content string
