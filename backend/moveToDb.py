import psycopg2
import pandas as pd
import numpy as np
import ast



# Connect to your database (adjust parameters accordingly)
conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="bruno",  # or your username
    password="your_password"  # if applicable
)
cur = conn.cursor()


create_textbook_table_query = """
CREATE TABLE IF NOT EXISTS textbooks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    author TEXT NOT NULL
);
"""
cur.execute(create_textbook_table_query)



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
cur.execute(chaptersTable)


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
cur.execute(embeddingTable)



df = pd.read_csv("/Users/javierzegada/Desktop/studyGuider/StudyGuider/bookAdders/csv/thinkpython2.csv")
title = "thinkpython2"
author = "Allen Downey"


# adding to textbook table
cur.execute("SELECT MAX(id) FROM textbooks")
max_id = cur.fetchone()[0]
next_id = (max_id + 1) if max_id is not None else 1
addRan = f"""
INSERT INTO textbooks (id, name, author)
VALUES ({next_id}, '{title}', '{author}');
"""
cur.execute(addRan)


# Loop through each row in the DataFrame and insert the data
for chapter_id, group in df.groupby('chapter'):

    chapterTitle = group['Chapter_Name'].iloc[0]
    

    # Insert into the chapters table
    insert_chapter_query = """
    INSERT INTO chapters (textbook_id, chapter_number, chapter_title)
    VALUES (%s, %s, %s)
    ON CONFLICT (textbook_id, chapter_number) DO NOTHING;
    """
    cur.execute(insert_chapter_query, (next_id, chapter_id, chapterTitle))

    # Now group contains only rows for the current chapter.
    for index, row in group.iterrows():


        
        # Convert your embedding list to a string if your database expects that format.
        chunkIndex = index
        embedding_str = row['text_vector_embeddings']
        chunk_text = row['chunk_text']

        insert_embedding_query = """
        INSERT INTO chapter_embeddings (textbook_id, chapter_number, chunk_index, embedding, chunk_text)
        VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(insert_embedding_query, (next_id, chapter_id, chunkIndex, embedding_str, chunk_text))


conn.commit()
cur.close()
conn.close()