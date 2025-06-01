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
    chat = ChatOpenAI(
        openai_api_base="http://localhost:4000",  # LiteLLM proxy URL
        model="gemma:2b",
        openai_api_key="EMPTY"
    )

    # Stream response token by token
    for chunk in chat.stream(message):
        print(chunk.content)
        yield chunk.content  # Yield only the content string
