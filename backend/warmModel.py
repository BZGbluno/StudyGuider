import requests

url = "http://host.docker.internal:11435/api/generate"
data = {
    "model": "llama3.1",
    "prompt": "warm up",
    "stream": False
}

requests.post(url, json=data)