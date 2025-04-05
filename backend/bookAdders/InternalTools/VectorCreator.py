import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm


class VectorEmbedder:

    def __init__(self, model_id:str, chunked_file:pd.DataFrame):

        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = AutoModel.from_pretrained(model_id).to(self.device)
        self.chunkedPdfDf = chunked_file

        self.embeddedDataFrame = None



    def _generate_embeddings(self, texts:str):

        # Tokenize and prepare inputs (you'll need to make sure tensors are also on the correct device)
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)
        
        # Get the embeddings from the model
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get the embeddings from the last hidden state (use mean pooling over tokens)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        
        embeddings = embeddings.cpu().numpy().tolist()
        return embeddings[0]
    


    def createEmbeddings(self):

        if self.chunkedPdfDf is None:
            raise Exception("Chunk Pdf missing: Make sure to create that first")

        # Enable the tqdm pandas integration
        tqdm.pandas()
        self.chunkedPdfDf['text_vector_embeddings'] = self.chunkedPdfDf['chunk_text'].astype(str).progress_apply(self._generate_embeddings)
        self.embeddedDataFrame = self.chunkedPdfDf
    
    def printEmbeddings(self):
        if self.chunkedPdfDf is None:
            raise Exception("Empty Embedded Data Frame: Make sure to create embeddings before printing")
        
        print(self.embeddedDataFrame.head())
    
    def getEmbeddingsDf(self):
        if self.embeddedDataFrame is None:
            raise Exception("Empty Embedded Data Frame: Make sure to create embeddings before printing")
        return self.embeddedDataFrame


        

        



    
