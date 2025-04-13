import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def testGenerateAPI():
    '''
    This test is meant to call the generate guido api in the way 
    it was meant for by passing prompt, textbook, and chapter
    '''
    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }

    response = requests.post(url=url, json=data)

    assert(response.status_code == 200)

    # parse in json
    chunk_data = response.json()

    assert "response" in chunk_data, "Key 'response' missing in JSON"


def testGenerateAPIwithVeryLargePrompt():
    '''
    This test is meant to call the generate guido api 
    using a very large prompt
    '''
    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program asfd  asf  asdf asf fasdf  sadf fas ffda f f f f f f f f f f f  f f f f f f f f f f f f f d d dd d d d d d d d d d d l l ?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }
    response = requests.post(url=url, json=data)
    body = response.json()

    assert(body['detail'] == 'Prompt too long: keep it below 50 words')
    assert(response.status_code == 400)



def testGenerateAPIwithFaultyTextbook():
    '''
    This test is meant to call the generate guido api 
    using a non existent textbook
    '''
    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "nivar",
        "chapter": "The Way of the Program"
    }
    response = requests.post(url=url, json=data)
    body = response.json()

    assert(body['detail'] == f"Chapter The Way of the Program not found or textbook nivar not found.")
    assert(response.status_code == 404)

def testLoadGenerateAPI():
    '''
    This function will test the concurrency of our
    application when it comes to generating with Guido
    It will perform 25 request using 10 threads
    '''

    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }

    def _sendRequest(url, data):
        try:
            response = requests.post(url, json=data)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def _loadTest(url, data, num_request, num_threads):
        responses = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(_sendRequest, url, data) for _ in range(num_request)]
            for future in as_completed(futures):
                responses.append(future.result())
        return responses
    
    numThreads = 10
    numRequest = 50
    
    startTime = time.time()
    responses = _loadTest(url, data, numRequest, numThreads)
    endTime = time.time()
    
    for response in responses:
        if response:
            assert(response.status_code == 200)
        else:
            print("Request failed.")
    

    print(f"This is the total time: {endTime-startTime}")

def main():

    testGenerateAPI()
    testGenerateAPIwithFaultyTextbook()
    testGenerateAPIwithVeryLargePrompt()
    testLoadGenerateAPI()
    
if __name__ == "__main__":

    main()

