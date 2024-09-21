import os
from langchain_chroma import Chroma
from .embeddings import embeddings
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from pinecone.grpc import PineconeGRPC as Pinecone

mode = os.environ.get("mode")
cloud = os.environ.get("pinecone_cloud")
region = os.environ.get("pinecone_region")
index_name = os.environ.get("pinecone_index_name")
pinecone_api_key = os.environ.get("pinecone_api_key")
pinecone_dimension = int(os.environ.get("pinecone_embedding_model_dimension"))

vector_store = (
    PineconeVectorStore(index_name=index_name, embedding=embeddings)
    if mode == "prod"
    else Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory="./local-vector-storage",
    )
)

if mode == "prod":
    pc = Pinecone(api_key=pinecone_api_key)
    indexes = pc.list_indexes().indexes
    found_indexes = list(filter(lambda index: index["name"] == index_name, indexes))

    if len(found_indexes) == 0:
        pc.create_index(
            name=index_name,
            dimension=pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=cloud,
                region=region,
            ),
        )
