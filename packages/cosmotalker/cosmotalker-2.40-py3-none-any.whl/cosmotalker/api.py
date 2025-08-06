# api.py
# Handles interactions with the Ollama REST API, including streaming support

import requests
import json

class api:
    def __init__(self, base_url="http://localhost:11434"):
        """Initialize the Ollama API client."""
        self.base_url = base_url
        self.model = "tinyllama"  # Default model, can be changed later

    def get_available_models(self):
        """Retrieve list of available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.RequestException as e:
            return {"error": f"Failed to fetch models: {str(e)}"}

    def send_prompt(self, prompt, stream=False):
        """Send a prompt to the Ollama API and return the response or stream."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload, stream=stream)
            response.raise_for_status()

            if stream:
                def generate():
                    for line in response.iter_lines():
                        if line:
                            yield json.loads(line.decode('utf-8')).get("response", "")
                return generate()
            else:
                return response.json().get("response", "No response received")
        except requests.RequestException as e:
            return f"Error: Could not connect to Ollama. Is it running? ({str(e)})"


