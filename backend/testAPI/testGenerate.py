import requests
import json
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def testGenerateAPI():
    url = 'http://0.0.0.0:8000/api/generate'

    data = {
        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }
    response = requests.post(url=url, json=data)
    chunk_data = response.json()

    print(chunk_data['response'])



def testGetAllTextBooks():
    url = 'http://0.0.0.0:8000/api/getTextbooks'

    response = requests.get(url=url)
    chunk_data = response.json()
    print(chunk_data['response'])


def testGetAllChapters():
    url = 'http://0.0.0.0:8000/api/getChapters'


    params = {
        "textbook": "thinkpython2"
    }

    response = requests.get(url=url, params=params)
    chunk_data = response.json()

    print(chunk_data['response'])

def testFlashCard():
    url = 'http://0.0.0.0:8000/api/generateFlashCard'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program",
        "count": 5
    }
    response = requests.post(url=url, json=data)
    chunk_data = response.json()

    print(chunk_data)


    flashcards = chunk_data["response"]

    for key, value in flashcards.items():
        question, answer_text = value
        print(f"{key}")
        print(f"Question: {question}")
        print(f"Answer: {answer_text}")
        print("\n")



def testSummary():
    url = 'http://0.0.0.0:8000/api/generateSummary'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }
    response = requests.post(url=url, json=data)
    chunk_data = response.json()

    print(chunk_data['response'])


# testSummary()
# testFlashCard()
# testGenerateAPI()
# testGetAllTextBooks()
# testGetAllChapters()


from concurrent.futures import ThreadPoolExecutor, as_completed

# def testLoad():

#     # url = 'http://0.0.0.0:8000/api/getChapters'


#     # params = {
#     #     "textbook": "thinkpython2"
#     # }

#     url = 'http://0.0.0.0:8000/api/generate'

#     params = {
#         "Content-Type": "application/json",
#         "prompt": "What is a program?",
#         "textbook": "thinkpython2",
#         "chapter": "The Way of the Program"
#     }


#     def send_request(url, params):
#         try:
#             response = requests.post(url, json=params, timeout=10)
#             return response
#         except Exception as e:
#             print(f"Error: {e}")
#             return None

#     def load_test(url, params, num_requests=50, num_threads=10):
#         responses = []
#         with ThreadPoolExecutor(max_workers=num_threads) as executor:
#             futures = [executor.submit(send_request, url, params) for _ in range(num_requests)]
#             for future in as_completed(futures):
#                 responses.append(future.result())
#         return responses
    
#     responses = load_test(url, params)
#     for response in responses:
#         if response:
#             print("Status Code:", response.status_code)
#         else:
#             print("Request failed.")

# start = time.time()

# testLoad()

# end = time.time()

# print(end-start)

# testGenerateAPI()