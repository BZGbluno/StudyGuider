import requests

def testSummary():
    '''
    This test the OpenAI endpoint that takes care of 
    creating a summary
    '''
    url = 'http://0.0.0.0:8000/api/generateSummary'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "Files"
    }
    response = requests.post(url=url, json=data)

    assert(response.status_code == 200)
    chunk_data = response.json()
    assert "response" in chunk_data, "Key 'response' missing in JSON"

def testInvalidTextbook():
    '''
    This attempt to make a summary on a textbook that does
    not exist therefore throwing a 404
    '''
    url = 'http://0.0.0.0:8000/api/generateSummary'

    data = {
        "Content-Type": "application/json",
        "textbook": "fake",
        "chapter": "Files"
    }
    response = requests.post(url=url, json=data)
    assert(response.status_code == 400)
    body = response.json()
    assert(body['detail'] == 'Invalid textbook or chapter title')

def testInvalidChapterTitle():
    '''
    This attempt to make summary on a chapter that does not exist
    therefore throwing a 404
    '''
    url = 'http://0.0.0.0:8000/api/generateSummary'

    data = {
        "Content-Type": "application/json",
        "textbook": "thinkpython2",
        "chapter": "fake"
    }
    response = requests.post(url=url, json=data)
    assert(response.status_code == 400)
    body = response.json()
    assert(body['detail'] == 'Invalid textbook or chapter title')

def main():
    # testSummary()
    testInvalidTextbook()
    testInvalidChapterTitle()
    
if __name__ == "__main__":
    main()