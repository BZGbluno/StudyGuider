import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class VectorEmbedder:
    '''
    This class handles the creation of vector embeddings for chunks of text
    using a DataFrame with a specific format.

    Expected Inputs:
    --------------------------------------

    DataFrame:
        Columns:
        - chapter: (int) Chapter number
        - chunk_text: (str) A chunk of text from the chapter
        - Chapter_Name: (str) The name/title of the chapter
    
    Embedding Model:
        Name: The name of the embedding model from hugging face

    Private Methods:
    -------------
    _generate_embeddings:
        Internal method that takes the text and creates embeddings for it

    Public Methods:
    -------------
    createEmbeddings:
        This method handles create embeddings for each chunk by calling generate embeddings for each chunk of text
    printEmbeddings:
        This will the head of the dataframe to sample view your new dataframe
    getEmbeddingsDf:
        This will retrieve the new dataframe
    '''

    def __init__(self, model_id:str, chunked_file:pd.DataFrame):

        # setting the model
        self.model = SentenceTransformer(model_id)

        # input dataframe
        self.chunkedPdfDf = chunked_file

        # embedded data frame
        self.embeddedDataFrame = None



    def _generate_embeddings(self, texts: str):
        embedding = self.model.encode(texts)
        return embedding.tolist()
    


    def createEmbeddings(self):

        # Enable the tqdm pandas integration to check progress
        tqdm.pandas()
        self.chunkedPdfDf['text_vector_embeddings'] = self.chunkedPdfDf['chunk_text'].astype(str).progress_apply(self._generate_embeddings)
        self.embeddedDataFrame = self.chunkedPdfDf
    
    def printEmbeddings(self):
        if self.embeddedDataFrame is None:
            raise Exception("Empty Embedded Data Frame: Make sure to create embeddings before printing")
        
        print(self.embeddedDataFrame.head())
    
    def getEmbeddingsDf(self):
        if self.embeddedDataFrame is None:
            raise Exception("Empty Embedded Data Frame: Make sure to create embeddings before retrieving")
        return self.embeddedDataFrame


        

        



    
