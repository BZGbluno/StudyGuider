import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import os
import httpx
import asyncpg
import asyncio


# OLLAMA_HOST=127.0.0.1:11435 ollama serve

# Load tokenizer and model
model_id = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# Use MPS if available (Macs), otherwise CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)


async def generate_embeddings(texts):
    return await asyncio.to_thread(_generate_embeddings_blocking, texts)

def _generate_embeddings_blocking(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy().tolist()

async def getModelResponse(prompt: str) -> str:
    url = "http://host.docker.internal:11435/api/generate"
    data = {
        "model": "llama3.1",
        "prompt": f"p{prompt}",
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        result = response.json()
        return result.get("response", "")


async def generate_Helper(prompt, chapter, textbook):
    embedding = await generate_embeddings(prompt)
    embedding = str(np.array(embedding).astype("float32")[0].tolist())

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
        return "Could not find matching chapter."

    textbook_id = res["textbook_id"]
    chapter_number = res["chapter_number"]

    rows = await conn.fetch("""
        SELECT chunk_text, embedding <-> $1 AS distance
        FROM chapter_embeddings
        WHERE textbook_id = $2 AND chapter_number = $3
        ORDER BY distance ASC
        LIMIT 2;
    """, embedding, textbook_id, chapter_number)

    await conn.close()


    context = "\n".join(row[0] for row in rows)
    prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer:"

    ans = await getModelResponse(prompt)

    return ans


