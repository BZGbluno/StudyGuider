import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import os
import httpx
import asyncpg
import asyncio
from fastapi import HTTPException


# OLLAMA_HOST=127.0.0.1:11435 ollama serve

# Load tokenizer and model
model_id = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# Use MPS if available (Macs), otherwise CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)


async def generate_embeddings(texts):
    '''
    This function will asynchronously run the function generate embeddings blocking
    '''
    return await asyncio.to_thread(_generate_embeddings_blocking, texts)


def _generate_embeddings_blocking(texts):
    '''
    This is a blocking function that will generate embeddings for any given text
    using the all-MiniLM-L6-v2 model
    '''

    try:
        # Check input type
        if not isinstance(texts, (str, list)):
            raise ValueError("Input must be a string or list of strings.")
        
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.cpu().numpy().tolist()
    
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None 


async def getModelResponse(prompt: str) -> str:
    '''
    This will provide a prompt to Ollama and return what Ollama
    generated
    '''

    url = "http://host.docker.internal:11435/api/generate"
    data = {
        "model": "llama3.1",
        "prompt": f"p{prompt}",
        "stream": False
    }
    
    try: 
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)


            if response.status_code != 200:
                return f"Error: {response.status_code}"
            
            result = response.json()

            return result.get("response", "")

    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Error: An unexpected issue occurred."


async def generate_Helper(prompt, chapter, textbook):
    '''
    This function will generate embeddings for a prompt then
    run similairity search on a chapters vector embeddings based
    on its textbook 
    '''
    
    embedding = await generate_embeddings(prompt)
    
    # embedding is none then return none
    if embedding == None:
        return None
    
    # set embedding to string of float32 values
    embedding = str(np.array(embedding).astype("float32")[0].tolist())

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)

        if not res:
            print("Could not find matching chapter.")
            return None

        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        rows = await conn.fetch("""
            SELECT chunk_text, embedding <-> $1 AS distance
            FROM chapter_embeddings
            WHERE textbook_id = $2 AND chapter_number = $3
            ORDER BY distance ASC
            LIMIT 2;
        """, embedding, textbook_id, chapter_number)

        if not rows:
            print("No rows found")
            return None
        

        # combine context and make a prompt
        context = "\n".join(row[0] for row in rows)
        prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer:"

        try:
            ans = await getModelResponse(prompt)

            if not ans:
                # Handle empty response
                print("Warning: Model returned an empty string.")
                raise HTTPException(status_code=500, detail="Empty response from model.")

        except Exception as e:
            print(f"Failed to get model response: {e}")
            raise HTTPException(status_code=500, detail="Model Generation Error.")

        return ans
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()


