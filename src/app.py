import os
import time
from pinecone import ServerlessSpec
from langchain.vectorstores import Pinecone as LangChainPinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

openai_api_key = os.environ.get("openai_api_key")
pinecone_cloud = os.environ.get("pinecone_cloud")
pinecone_region = os.environ.get("pinecone_region")
