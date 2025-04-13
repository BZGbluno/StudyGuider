import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def testFlashCard():
    '''
    This will test generating 5 cards and will return successful if 
    at least 1 card generated correcly.
    '''
    url = 'http://0.0.0.0:8000/api/generateFlashCard'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "Files",
        "count": 10
    }
    response = requests.post(url=url, json=data)
    assert(response.status_code == 200)
    chunk_data = response.json()
    assert "response" in chunk_data, "Key 'response' missing in JSON"
    assert(type(chunk_data['response']) == dict)
    print(f"The success rate is: {(len(chunk_data['response'])/10) * 100}")


def testFlashCardWithFaultyTextbook():
    '''
    This will test generating 10 cards with a faulty textbook
    therefore throwing a 400 error
    '''
    url = 'http://0.0.0.0:8000/api/generateFlashCard'

    data = {
        "Content-Type": "application/json",
        "textbook": "fake",
        "chapter": "Files",
        "count": 10
    }
    response = requests.post(url=url, json=data)
    assert(response.status_code == 400)
    body = response.json()
    assert(body['detail'] == "Invalid textbook or chapter name")


def testFlashCardWithFaultyChapter():
    '''
    This will test generating 10 cards with a faulty chapter name
    therefore throwing a 400 error
    '''
    url = 'http://0.0.0.0:8000/api/generateFlashCard'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "fake000",
        "count": 10
    }
    response = requests.post(url=url, json=data)
    assert(response.status_code == 400)
    body = response.json()
    assert(body['detail'] == "Invalid textbook or chapter name")



def testLoadFlashCards():
    url = 'http://0.0.0.0:8000/api/generateFlashCard'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "Files",
        "count": 10
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
    numRequest = 10
    
    startTime = time.time()
    responses = _loadTest(url, data, numRequest, numThreads)
    endTime = time.time()
    for response in responses:
        if response:
            assert(response.status_code == 200)
            chunk_data = response.json()
            assert "response" in chunk_data, "Key 'response' missing in JSON"
            assert(type(chunk_data['response']) == dict)
            print(f"The success rate is: {(len(chunk_data['response'])/10) * 100}")
            
        else:
            print("Request failed.")

    print(f"This is the total time: {endTime-startTime}")




def main():
    testFlashCard()
    testFlashCardWithFaultyTextbook()
    testFlashCardWithFaultyChapter()
    testLoadFlashCards()


if __name__ == "__main__":
    main()