import os
import psycopg2
import time
import asyncpg
import asyncio

max_retries = 10
retry_delay = 2
async def init_db():
    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD")
                )


            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            create_textbook_table_query = """
            CREATE TABLE IF NOT EXISTS textbooks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            );
            """
            await conn.execute(create_textbook_table_query)



            chaptersTable = """
            CREATE TABLE chapters (
                textbook_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                chapter_title TEXT NOT NULL,
                PRIMARY KEY (textbook_id, chapter_number),
                FOREIGN KEY (textbook_id) REFERENCES textbooks (id)
                    ON DELETE CASCADE
            );
            """
            await conn.execute(chaptersTable)


            embeddingTable = """
            CREATE TABLE IF NOT EXISTS chapter_embeddings (
                textbook_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding vector(384) NOT NULL,
                chunk_text TEXT NOT NULL,
                PRIMARY KEY (textbook_id, chapter_number, chunk_index),
                FOREIGN KEY (textbook_id, chapter_number) REFERENCES chapters (textbook_id, chapter_number)
                    ON DELETE CASCADE
            );
            """
            await conn.execute(embeddingTable)

            usersTable = """
            CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            provider VARCHAR(50),
            provider_id VARCHAR(255),
            last_login TIMESTAMP
            );
            """
            await conn.execute(usersTable)

            await conn.close()

            print("✅ Created All Tables!")
            break

        except Exception as e:
            print(f"❌ Attempt {attempt+1}/{max_retries}: Database not ready, retrying in 2s...")
            await asyncio.sleep(retry_delay)
            

asyncio.run(init_db())