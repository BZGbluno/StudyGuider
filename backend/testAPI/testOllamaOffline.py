import requests
def testGenerateAPIwithOllamaDown():
    '''
    This test is meant to call the generate guido api 
    when Ollama server is down
    '''
    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }
    response = requests.post(url=url, json=data)
    body = response.json()

    assert(body['detail'] == f"Failed to connect to Ollama: All connection attempts failed")
    assert(response.status_code == 503)