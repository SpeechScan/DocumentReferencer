import os
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone

pc = Pinecone(api_key=os.getenv("pinecone_api_key"))

index_name = "example-index"
index = pc.Index(index_name)


