import requests
import os
OLLAMA_HOST  = os.getenv("OLLAMA_HOST")
OLLAMA_PORT  = os.getenv("OLLAMA_PORT")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")    
TIMEOUT_SEC   = float(os.getenv("OLLAMA_TIMEOUT_SEC"))
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

data = {
    "model": "llama3.1",
    "prompt": "warm up",
    "stream": False
}

requests.post(OLLAMA_URL, json=data)