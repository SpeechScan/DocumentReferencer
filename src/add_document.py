import os
import boto3
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

def get_pdf_loader(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader


def chunk_pdf(pdf_loader, chunk_size=10):
    page = []
    for doc in pdf_loader.lazy_load():
        page.append(doc)
        if len(page) >= chunk_size:
            yield page
            page = []
    # Yield any remaining pages after the loop ends
    if page:
        yield page

def section_chunk(chunk, section_size = 1000, section_overlap = 200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=section_size, chunk_overlap=section_overlap
    )
    splits = text_splitter.split_documents(chunk)
    return splits

def embed_sections(sections, username):
    index_name = os.environ.get("pinecone_index_name")
    cloud = os.environ.get("pinecone_cloud")
    region = os.environ.get("pinecone_region")
    pinecone_api_key = os.environ.get("pinecone_api_key")
    pinecone_embedding_model = os.environ.get("pinecone_embedding_model_name")
    pinecone_dimension = int(os.environ.get("pinecone_embedding_model_dimension"))

    pc = Pinecone(api_key=pinecone_api_key)
    indexes = pc.list_indexes().indexes
    found_indexes = filter(lambda index: index["name"] == index_name, indexes)

    if found_indexes == 0:
        pc.create_index(
            name=index_name,
            dimension=pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=cloud,
                region=region,
            ),
        )

    # Initialize a LangChain embedding object.
    embeddings = PineconeEmbeddings(
        model=pinecone_embedding_model, pinecone_api_key=pinecone_api_key
    )

    # Embed each chunk and upsert the embeddings into your Pinecone index.
    PineconeVectorStore.from_documents(
        documents=sections,
        index_name=index_name,
        embedding=embeddings,
        namespace=username,
    )

def store_in_vector_store(file_path, username):
    pdf_loader = get_pdf_loader(file_path)
    for chunk in chunk_pdf(pdf_loader):
        sections = section_chunk(chunk)
        embed_sections(sections, username)

def store_in_file_store(file_path, username):
    bucket_name = os.environ.get("s3_bucket")
    object_name = f"{username}/{os.path.basename(file_path)}"

    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket_name, object_name)

def main():
    username = "cv"
    doc_path = "./cv.pdf"
    store_in_vector_store(doc_path, username)
    store_in_file_store(doc_path, username)


if __name__ == "__main__":
    main()
