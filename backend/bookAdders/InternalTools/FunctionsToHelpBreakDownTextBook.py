import pandas as pd
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re




def pdfToString(pathToPdf:str):

    loader = PyPDFLoader(pathToPdf)
    documents = loader.load()
    combined_text = "\n".join([doc.page_content for doc in documents])

    return combined_text

    

def regex_text_splitter(text, pattern=r'\nChapter\s+\d+\s*[:.-]?\s*\n', keep_separator=False):
    """
    Splits the text using the given regex pattern.
    If keep_separator is True, the split separators are included in the chunks.
    """
    # Split text by pattern
    parts = re.split(pattern, text)
    if keep_separator:
        # Find all separators
        separators = re.findall(pattern, text)
        # Combine parts with their corresponding separators
        chunks = []
        for i, part in enumerate(parts):
            if i < len(separators):
                chunks.append(part + separators[i])
            else:
                chunks.append(part)
        return chunks
    else:
        return parts
    

def removeAnythingBeforeContent(text:str):

    index = text.lower().find("contents")

    if index != -1:
        # Slice the text starting from the word "contents"
        cleaned_text = text[index:]
    else:
        # If the word "contents" is not found, use the original text
        cleaned_text = text
    
    return cleaned_text


def splitIntoChunks_to_MapToChapter(chapters:list):
    chapterChunksMap = {}

    # Create a text splitter instance with desired chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    for i, chapter in enumerate(chapters, start=1):
        chunks = text_splitter.split_text(chapter)
        
        chapterChunksMap[i] = chunks

    return chapterChunksMap


def MapOfChapterWithChunks_to_DataFrame(map_of_chapter_with_chunks:dict):

    data = []

    # Iterate over the chapters and their chunks
    for chapter, chunks in map_of_chapter_with_chunks.items():
        for idx, chunk in enumerate(chunks, start=1):
            data.append({
                'chapter': chapter,
                'chunk_index': idx,
                'chunk_text': chunk
            })

    # Create the DataFrame
    df = pd.DataFrame(data)

    return df

def RemoveAppendixFromFinalChapter(chapters, finalChapterIndex):
    index1 = chapters[finalChapterIndex].lower().find("appendix")
    chapters[finalChapterIndex] = chapters[finalChapterIndex][:index1]
    chapters = chapters[1:]

    return chapters
