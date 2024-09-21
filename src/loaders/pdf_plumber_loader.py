from langchain_community.document_loaders import PDFPlumberLoader

def get_pdf_plumber_loader(file_path):
    return PDFPlumberLoader(file_path)