import os
from .objects import get_vector_store
from .objects import s3_client
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

username = os.environ.get("username")
doc_path = os.environ.get("doc_path")

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


def section_chunk(chunk, section_size=1000, section_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=section_size, chunk_overlap=section_overlap
    )
    splits = text_splitter.split_documents(chunk)
    return splits


def embed_sections(sections, doc_path, start_from):
    # Ensure that the sections are in the correct format
    if not sections or len(sections) == 0:
        print("No sections to upsert!")
        return start_from

    # Generate IDs starting from `start_from`
    ids = [f"{doc_path}-{i}" for i in range(start_from, start_from + len(sections))]

    # Upsert sections with incremental IDs
    vector_store = get_vector_store(username)
    vector_store.add_documents(sections, ids)
    # Return the updated start_from value for the next chunk
    return start_from + len(sections)


def store_in_vector_store():
    pdf_loader = get_pdf_loader(doc_path)
    start_from = 0
    for chunk in chunk_pdf(pdf_loader):
        sections = section_chunk(chunk)
        start_from = embed_sections(sections, doc_path, start_from)


def store_in_file_store():
    bucket_name = os.getenv("s3_bucket")
    object_name = f"{username}/{os.path.basename(doc_path)}"
    s3_client.upload_file(doc_path, bucket_name, object_name)


def main():
    store_in_vector_store()
    store_in_file_store()

if __name__ == "__main__":
    main()
