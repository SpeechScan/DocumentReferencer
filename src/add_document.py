from langchain_community.document_loaders import PDFPlumberLoader


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


def main():
    pdf_loader = get_pdf_loader("./example.pdf")
    for chunk in chunk_pdf(pdf_loader):
        # Process the chunk
        print(f"Processing chunk with {len(chunk)} pages")


if __name__ == "__main__":
    main()
