import os
from .objects import get_vector_store
from .objects import s3_client

username = os.environ.get("username")
doc_path = os.environ.get("doc_path")

def delete_in_vector_store():
    vector_store = get_vector_store(username)
    vector_store.delete_documents(doc_path)

def delete_in_file_store():
    bucket_name = os.environ.get("s3_bucket")
    object_name = f"{username}/{os.path.basename(doc_path)}"
    s3_client.delete_object(Bucket=bucket_name, Key=object_name)

def main():
    delete_in_vector_store()
    delete_in_file_store()

if __name__ == "__main__":
    main()
