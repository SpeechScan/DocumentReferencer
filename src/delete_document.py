import os
import boto3
from pinecone.grpc import PineconeGRPC as Pinecone

username = os.environ.get("username")

def delete_in_vector_store(file_path):
    pinecone_api_key = os.environ.get("pinecone_api_key")
    pinecone_index = os.environ.get("pinecone_index_name")

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(pinecone_index)

    for ids in index.list(namespace=username, prefix=file_path):
        index.delete(ids=ids, namespace=username)

def delete_in_file_store(file_name):
    bucket_name = os.environ.get("s3_bucket")
    object_name = f"{username}/{os.path.basename(file_name)}"

    s3 = boto3.client("s3")
    s3.delete_object(Bucket=bucket_name, Key=object_name)

def main():
    file_path = "./cv.pdf"
    delete_in_vector_store(file_path)
    delete_in_file_store(file_path)

if __name__ == "__main__":
    main()
