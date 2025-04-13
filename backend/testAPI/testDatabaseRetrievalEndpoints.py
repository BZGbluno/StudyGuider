import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed



def testGetAllTextBooks():
    '''
    This test retrieving all the textbooks from the database
    '''
    url = 'http://0.0.0.0:8000/api/getTextbooks'

    response = requests.get(url=url)
    assert(response.status_code == 200)
    res = response.json()
    assert "response" in res, "Key 'response' missing in JSON"




def testLoadGetAllTextBooks():
    '''
    This test 50 users retrieving all the textbooks from the database 
    concurrently
    '''
    url = 'http://0.0.0.0:8000/api/getTextbooks'


    def _sendRequest(url):
        try:
            response = requests.get(url)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _loadTest(url,num_request, num_threads):
        responses = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(_sendRequest, url) for _ in range(num_request)]
            for future in as_completed(futures):
                responses.append(future.result())
        return responses

    startTime = time.time()
    responses = _loadTest(url, num_request=50, num_threads=10)
    endTime = time.time()

    for response in responses:
        if response:
            assert(response.status_code == 200)
            chunk_data = response.json()
            assert "response" in chunk_data, "Key 'response' missing in JSON"
            assert(type(chunk_data['response']) == list)
        else:
            print("Request failed.")

    print(f"This is the total time: {endTime-startTime}")



def testGetAllChapters():
    '''
    This will retrieve all the chapters given a textbook
    '''
    url = 'http://0.0.0.0:8000/api/getChapters'


    params = {
        "textbook": "thinkpython2"
    }

    response = requests.get(url=url, params=params)

    assert(response.status_code == 200)
    chunk_data = response.json()
    assert "response" in chunk_data, "Key 'response' missing in JSON"
    assert(type(chunk_data['response']) == list)



def testGetAllChaptersOnNonExistentTextbook():
    '''
    This will attempt to retrieve the chapters on a textbook 
    that does not exist therefore causing a 404
    '''
    url = 'http://0.0.0.0:8000/api/getChapters'


    params = {
        "textbook": "fake"
    }

    response = requests.get(url=url, params=params)
    assert(response.status_code == 404)
    body = response.json()
    assert(body['detail'] == 'Textbook not found')



def testLoadGetAllChapters():
    '''
    This will retrieve all the chapters given a textbook concurrently
    with 50 other users
    '''

    url = 'http://0.0.0.0:8000/api/getChapters'


    params = {
        "textbook": "thinkpython2"
    }

    def _sendRequest(url, params):
        try:
            response = requests.get(url, params=params)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _loadTest(url,params, num_request, num_threads):
        responses = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(_sendRequest, url, params) for _ in range(num_request)]
            for future in as_completed(futures):
                responses.append(future.result())
        return responses

    startTime = time.time()
    responses = _loadTest(url, params, num_request=50, num_threads=10)
    endTime = time.time()

    for response in responses:
        if response:
            assert(response.status_code == 200)
            chunk_data = response.json()
            assert "response" in chunk_data, "Key 'response' missing in JSON"
            assert(type(chunk_data['response']) == list)
        else:
            print("Request failed.")

    print(f"This is the total time: {endTime-startTime}")


def main():

    testGetAllChapters()
    testGetAllTextBooks()
    testLoadGetAllChapters()
    testLoadGetAllTextBooks()
    testGetAllChaptersOnNonExistentTextbook()
if __name__ == "__main__":
    main()







