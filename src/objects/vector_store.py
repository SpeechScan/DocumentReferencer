import os
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from .embeddings import embeddings  # Ensure this is correctly set up for your use case

# Common configurations
mode = os.getenv("mode")
index_name = os.getenv("pinecone_index_name")
pinecone_api_key = os.getenv("pinecone_api_key")
pinecone_dimension = int(os.getenv("pinecone_embedding_model_dimension", 1536))
cloud = os.getenv("pinecone_cloud")
region = os.getenv("pinecone_region")


# Production class using Pinecone
class PineconeVectorStoreClient:
    def __init__(self, index_name, embedding, namespace):
        self.index_name = index_name
        self.embedding = embedding
        self.namespace = namespace
        self.pinecone_client = Pinecone(
            api_key=pinecone_api_key
        )

        # Check and create the index if it doesn't exist
        self.ensure_index_exists()
        print(index_name, embedding, pinecone_api_key)

        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embedding,
            pinecone_api_key=pinecone_api_key,
        )

    def ensure_index_exists(self):
        indexes = self.pinecone_client.list_indexes().indexes
        found_indexes = list(
            filter(lambda index: index["name"] == self.index_name, indexes)
        )

        print(found_indexes)

        if not found_indexes:
            self.pinecone_client.create_index(
                name=self.index_name,
                dimension=pinecone_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region,
                ),
            )

    def add_documents(self, documents, ids):
        self.vector_store.add_documents(
            documents=documents, ids=ids, namespace=self.namespace
        )

    def delete_documents(self, file_path):
        index = self.pinecone_client.Index(self.index_name)
        for ids in index.list(namespace=self.namespace, prefix=file_path):
            index.delete(ids=ids, namespace=self.namespace)

    def as_retriever(self):
        print(self.namespace)
        return self.vector_store.as_retriever(namespace=self.namespace, index_name=self.index_name)


# Development class using Chroma
class ChromaVectorStoreClient:
    def __init__(self, username):
        self.collection_name = f"example_collection_{username}"
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory='dev_vector_db'
        )

    def add_documents(self, documents, ids):
        ids = self.vector_store.add_documents(documents=documents, ids=ids)
        return ids

    def delete_documents(self, file_path):
        docs = self.vector_store.get(where={"file_path": file_path})
        self.vector_store.delete(docs['ids'])

    def as_retriever(self):
        return self.vector_store.as_retriever()


# Factory function to initialize the correct vector store based on mode
def get_vector_store(username):
    if mode == "prod":
        return PineconeVectorStoreClient(
            index_name=index_name, embedding=embeddings, namespace=username
        )
    else:
        return ChromaVectorStoreClient(username=username)
