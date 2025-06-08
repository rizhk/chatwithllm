from langchain_huggingface import HuggingFaceEndpoint
import requests
from dotenv import load_dotenv
load_dotenv()

import os
HF_API = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_API_URL = os.getenv("HUGGINGFACEHUB_API_URL")
class CustomHuggingFaceEndpoint(HuggingFaceEndpoint):
    def _call(self, prompt: str, stop: list = None, run_manager=None, **kwargs) -> str:
        # Base URL from endpoint_url
        url = self.endpoint_url.rstrip("/") + "/v1/completions"

        # Define the payload
        payload = {
            "model": "gpt2.gguf",  # specify your model name if needed
            "prompt": prompt,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            # Add more params as needed
        }

        # Define headers manually inside the call
        headers = {
            "Authorization": f"Bearer {HF_API}",
            "Content-Type": "application/json"
        }

        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)

        # Raise for errors
        response.raise_for_status()

        # Parse JSON
        data = response.json()

        # Return generated text
        return data["choices"][0]["text"]
    
    
    # Create LLM instance
llm = CustomHuggingFaceEndpoint(
    endpoint_url=HF_API_URL, 
    max_new_tokens=50,
    temperature=0.7,
)

# Run inference
response = llm.invoke("Hello, how are you?")
print(response)