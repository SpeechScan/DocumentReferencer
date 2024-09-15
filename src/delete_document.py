import os
from pinecone.grpc import PineconeGRPC as Pinecone

username = os.environ.get("username")

def main():
    pinecone_api_key = os.environ.get("pinecone_api_key")
    pinecone_index = os.environ.get("pinecone_index_name")
    file_path = "./kekw.pdf"

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(pinecone_index)

    for ids in index.list(namespace=username, prefix=file_path):
        index.delete(ids=ids, namespace=username)

if __name__ == "__main__":
    main()
