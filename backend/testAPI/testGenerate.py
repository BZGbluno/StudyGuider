import requests
import json


def testGenerateAPI():
    url = 'http://127.0.0.1:8000/api/generate'

    data = {

        "Content-Type": "application/json",
        "prompt": "What is a program?",
        "textbook": "thinkpython2",
        "chapter": "The Way of the Program"
    }

    response = requests.get(url=url, json=data)
    chunk_data = response.json()

    print(chunk_data['response'])

def testGetAllTextBooks():
    url = 'http://127.0.0.1:8000/api/getTextbooks'


    response = requests.get(url=url)
    chunk_data = response.json()

    print(chunk_data['response'])




def testGetAllChapters():
    url = 'http://127.0.0.1:8000/api/getChapters'


    data = {

        "Content-Type": "application/json",
        "textbook": "thinkpython2"
    }

    response = requests.get(url=url, json=data)
    chunk_data = response.json()

    print(chunk_data['response'])


testGenerateAPI()
testGetAllTextBooks()
testGetAllChapters()