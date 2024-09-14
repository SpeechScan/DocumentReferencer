import os
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

def embed_sections(sections):
    index_name = os.environ.get("pinecone_index_name")
    cloud = os.environ.get("pinecone_cloud")
    region = os.environ.get("pinecone_region")
    pinecone_api_key = os.environ.get("pinecone_api_key")

    pc = Pinecone(api_key=pinecone_api_key)
    indexes = pc.list_indexes().indexes
    found_indexes = filter(lambda index: index["name"] == index_name, indexes)

    if found_indexes == 0:
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=cloud,
                region=region,
            ),
        )

    # Initialize a LangChain embedding object.
    model_name = "multilingual-e5-large"
    embeddings = PineconeEmbeddings(model=model_name, pinecone_api_key=pinecone_api_key)

    # Embed each chunk and upsert the embeddings into your Pinecone index.
    PineconeVectorStore.from_documents(
        documents=sections,
        index_name=index_name,
        embedding=embeddings,
        namespace="wondervector5000",
    )

def store_in_vector_store(file_path):
    pdf_loader = get_pdf_loader(file_path)
    for chunk in chunk_pdf(pdf_loader):
        sections = section_chunk(chunk)
        embed_sections(sections)

def store_in_file_store(file_path):
    

def main():
    doc_path = "./example.pdf"
    store_in_vector_store(doc_path)
    


if __name__ == "__main__":
    main()
