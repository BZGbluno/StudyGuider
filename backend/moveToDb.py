import pandas as pd
import os
import asyncpg
import asyncio

async def fillTables():
    retry_delay = 2
    max_retries = 10

    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD")
            )

            allTextBooks = pd.read_csv("/csv/main.csv")

            for textbook, creator in zip(allTextBooks['Textbooks'], allTextBooks['Author']):
                df = pd.read_csv(f"/csv/{textbook}.csv")

                title = str(textbook)
                author = str(creator)

                result = await conn.fetchval("SELECT MAX(id) FROM textbooks")
                next_id = (result + 1) if result is not None else 1

                await conn.execute("""
                    INSERT INTO textbooks (id, title, author)
                    VALUES ($1, $2, $3);
                """, next_id, title, author)

                for chapter_id, group in df.groupby('chapter'):
                    chapter_title = group['Chapter_Name'].iloc[0]

                    await conn.execute("""
                        INSERT INTO chapters (textbook_id, chapter_number, chapter_title)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (textbook_id, chapter_number) DO NOTHING;
                    """, next_id, chapter_id, chapter_title)

                    for index, row in group.iterrows():
                        embedding_str = row['text_vector_embeddings']
                        chunk_text = row['chunk_text']

                        await conn.execute("""
                            INSERT INTO chapter_embeddings (textbook_id, chapter_number, chunk_index, embedding, chunk_text)
                            VALUES ($1, $2, $3, $4, $5);
                        """, next_id, chapter_id, index, embedding_str, chunk_text)

            await conn.close()
            print("✅ All Data Was Added To Tables")
            break

        except Exception as e:
            print(f"❌ Attempt {attempt+1}/{max_retries}: {e} — retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)

asyncio.run(fillTables())
