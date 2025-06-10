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

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                **kwargs
            }
        }

        response = requests.post(f"{self.endpoint_url}", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Handle response format: it's a list with one item
        return data[0]["generated_text"]

    def _stream(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> Iterator[str]:
        """Stream tokens one-by-one from the model."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                "stream": True,  # Enable streaming if supported by server
                **kwargs
            }
        }

        with requests.post(f"{self.endpoint_url}/generate", headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        # Try parsing as JSON (some models return token objects)
                        decoded_line = line.decode("utf-8")
                        if '"token"' in decoded_line:
                            token_data = json.loads(decoded_line)
                            yield token_data["token"]["text"]
                    except json.JSONDecodeError:
                        # If not valid JSON, treat whole line as text
                        yield decoded_line

# Replace with your actual endpoint URL from Hugging Face
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

llm = HFCompletionLLM(
    endpoint_url=HF_ENDPOINT_URL,
    token=HF_TOKEN,
    max_new_tokens=150
)
