import os
from .objects import file_store
from .objects import vector_store
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

username = os.environ.get("username")

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
    vector_store.add_documents(documents=sections, ids=ids, namespace=username)
    # Return the updated start_from value for the next chunk
    return start_from + len(sections)


def store_in_vector_store(file_path):
    pdf_loader = get_pdf_loader(file_path)
    start_from = 0
    for chunk in chunk_pdf(pdf_loader):
        sections = section_chunk(chunk)
        start_from = embed_sections(sections, file_path, start_from)


def store_in_file_store(file_path):
    object_name = f"{username}/{os.path.basename(file_path)}"
    file_store.upload_file(file_path, object_name)


def main():
    doc_path = "./kekw.pdf"
    store_in_vector_store(doc_path)
    store_in_file_store(doc_path)

if __name__ == "__main__":
    main()
