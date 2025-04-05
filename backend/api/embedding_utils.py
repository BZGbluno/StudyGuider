import psycopg2
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import requests



# Load tokenizer and model
model_id = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# Use MPS if available (Macs), otherwise CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)

def generate_embeddings(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy().tolist()


def getModelResponse(prompt):
    # Define the URL for the local Ollama server (assuming it's running locally)
    url = "http://localhost:11434/api/generate"


    # Create a payload with the model and the input query
    data = {
        "model": "llama3.1",
        "prompt": f"p{prompt}",
        "stream": False
    }

    # Send the POST request with the JSON data, and use stream=True to handle streamed respons
    response = requests.post(url, json=data, stream=False)

    result = response.json()
    full_response = result.get("response", "")

    return full_response



def generate_Helper(prompt, chapter, textbook):
    embedding = generate_embeddings(prompt)

    embedding = str(np.array(embedding).astype("float32")[0].tolist())

    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="bruno",
        password="your_password"
    )
    cur = conn.cursor()


    findTextBookandChapterQuery = """
    SELECT 
        c.textbook_id,
        c.chapter_number
    FROM chapters c
    JOIN textbooks t ON c.textbook_id = t.id
    WHERE t.name = %s AND c.chapter_title = %s;
    """

    cur.execute(findTextBookandChapterQuery, (textbook, chapter))
    res = cur.fetchone()

    textbook_id = res[0]
    chapter_number = res[1]


    query = """
    SELECT 
        chunk_text,
        embedding <-> %s AS distance
    FROM chapter_embeddings
    WHERE textbook_id = %s AND chapter_number = %s
    ORDER BY distance ASC
    LIMIT 2;
    """
    cur.execute(query, (embedding, textbook_id, chapter_number))
    results = cur.fetchall()
    cur.close()
    conn.close()


    context = "\n".join(row[0] for row in results)
    prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer:"

    ans = getModelResponse(prompt)

    return ans


