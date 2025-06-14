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
from HFCompletionLLM import llm

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


# Point to your local LiteLLM proxy
def chat_stream(message: str):
    result = llm.invoke(message)
    return result  # Just returns string — NOT a generator
