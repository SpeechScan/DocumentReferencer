from .recursive_text_splitter import get_recursive_text_splitter

def get_text_splitter(chunk_size, chunk_overlap):
    return get_recursive_text_splitter(chunk_size, chunk_overlap)