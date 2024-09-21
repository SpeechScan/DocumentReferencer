import os
from langchain_pinecone import PineconeEmbeddings
from langchain_ollama import OllamaEmbeddings

mode = os.environ.get("mode")
pinecone_api_key = os.environ.get("pinecone_api_key")
pinecone_embedding_model = os.environ.get("pinecone_embedding_model_name")

embeddings = (
    PineconeEmbeddings(
        model=pinecone_embedding_model, pinecone_api_key=pinecone_api_key
    )
    if mode == "prod"
    else OllamaEmbeddings(
        model="nomic-embed-text"
    )
)
