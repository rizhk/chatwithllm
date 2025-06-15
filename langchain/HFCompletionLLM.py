from langchain_core.language_models import LLM
from typing import Optional, List, Dict, Any, Iterator
import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

class HFCompletionLLM(LLM):
    endpoint_url: str
    token: str
    max_new_tokens: int = 100

    @property
    def _llm_type(self) -> str:
        return "custom_huggingface_completion"

    @property
    def _identifying_params(self) -> Dict[str, object]:
        return {
            "endpoint_url": self.endpoint_url,
            "max_new_tokens": self.max_new_tokens
        }

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    # Simulate chat template manually
        formatted_prompt = prompt.lstrip('\n') 

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                **kwargs
            }
        }

        response = requests.post(f"{self.endpoint_url}", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        generated_text = data[0].get("generated_text", "")
        
        answer = generated_text[len(formatted_prompt):].strip()

        return answer
        # Handle response format: it's a list with one item
        # return data[0]["generated_text"]

    def _stream(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> Iterator[str]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # Only keep JSON-serializable values in payload
        safe_kwargs = {
            k: v for k, v in kwargs.items()
            if isinstance(v, (str, int, float, bool, type(None))) or
            isinstance(v, (list, dict))  # Recursively check later if needed
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                "stream": True,
                **safe_kwargs  # Only pass serializable keys
            }
        }

        with requests.post(f"{self.endpoint_url}", headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    yield decoded_line
                    
                             
# Replace with your actual endpoint URL from Hugging Face
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

llm = HFCompletionLLM(
    endpoint_url=HF_ENDPOINT_URL,
    token=HF_TOKEN,
    max_new_tokens=150
)
