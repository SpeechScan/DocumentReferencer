import os
from src.objects import get_vector_store
from src.objects import s3_client
from src.splitters import get_text_splitter
from src.loaders import get_pdf_loader
from src.parsers.models import Statement
from src.parsers import get_json_parser
from src.prompts import get_inconcistencies_prompt
from src.runnables import passthrough, RunnableLambda
from src.objects import llm


class DocumentService:
    def __init__(self) -> None:
        self.username = os.environ.get("username")
        self.doc_path = os.environ.get("doc_path")
        self.bucket_name = os.environ.get("s3_bucket")

        self.vector_store = get_vector_store(self.username)

    def add_document(self):
        pdf_loader = get_pdf_loader(self.doc_path)
        start_from = 0
        for chunk in self.__chunk_pdf(pdf_loader):
            sections = self.__section_chunk(chunk)
            print(sections, start_from)
            start_from = self.__embed_sections(sections, start_from)
        s3_client.upload_file(self.doc_path, self.bucket_name, self.__get_file_name())

    def find_inconcistency(self, statement):
        try:
            parser = get_json_parser(Statement)
            prompt = get_inconcistencies_prompt(parser)

            chain = (
                {
                    "context": self.vector_store.as_retriever()
                    | DocumentService.format_docs,
                    "statement": passthrough,
                }
                | RunnableLambda(DocumentService.__print_body)
                | prompt
                | llm
                | parser
            )

            response = chain.invoke(statement)
            print("response:", response)
        except Exception as e:
            print(str(e))

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    @staticmethod
    def __print_body(prompt):
        print("prompt:", prompt)
        return prompt

    def delete_document(self):
        self.vector_store.delete_documents(self.doc_path)
        s3_client.delete_object(Bucket=self.bucket_name, Key=self.__get_file_name())

    def __get_file_name(self):
        object_name = f"{self.username}/{os.path.basename(self.doc_path)}"
        return object_name

    def __chunk_pdf(self, pdf_loader, chunk_size=10):
        page = []
        for doc in pdf_loader.lazy_load():
            page.append(doc)
            if len(page) >= chunk_size:
                yield page
                page = []
        # Yield any remaining pages after the loop ends
        if page:
            yield page

    def __section_chunk(self, chunk, section_size=1000, section_overlap=200):
        text_splitter = get_text_splitter(
            chunk_size=section_size, chunk_overlap=section_overlap
        )
        splits = text_splitter.split_documents(chunk)
        return splits

    def __embed_sections(self, sections, start_from):
        # Ensure that the sections are in the correct format
        if not sections or len(sections) == 0:
            print("No sections to upsert!")
            return start_from

        # Generate IDs starting from `start_from`
        ids = [
            f"{self.doc_path}-{i}"
            for i in range(start_from, start_from + len(sections))
        ]

        # Upsert sections with incremental IDs
        self.vector_store.add_documents(sections, ids)
        # Return the updated start_from value for the next chunk
        return start_from + len(sections)
