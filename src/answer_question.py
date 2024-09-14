from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_pinecone import Pinecone
from langchain_pinecone import PineconeEmbeddings
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import os

class Statement(BaseModel):
    statement: str = Field(description="A statement said by a person")
    isStatementTrue: bool = Field(description="Can statement be confirmed by your knowledge?")
    rejectionReasons: List[str] = Field(description="Array of sections from your knowledge based on which you rejected the statement. If statement is not false and can be confirmed by your knowledge, then make this array empty.")

def format_sections(sections):
    return "\n\n".join([d.page_content for d in sections])

def main():
    username = "aloof"
    openai_api_key = os.environ.get("openai_api_key")
    openai_model_name = os.environ.get("openai_model_name")

    pinecone_api_key = os.environ.get("pinecone_api_key")
    pinecone_index = os.environ.get("pinecone_index_name")
    pinecone_embedding_model = os.environ.get("pinecone_embedding_model_name")

    # Initialize a LangChain object for chatting with the LLM
    # without knowledge from Pinecone.
    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=openai_model_name,
        temperature=0.0,
    )

    embedding = PineconeEmbeddings(
        model=pinecone_embedding_model, pinecone_api_key=pinecone_api_key
    )
    pc = Pinecone(pinecone_api_key=pinecone_api_key, embedding=embedding)
    vector_store = pc.from_existing_index(namespace=username, index_name=pinecone_index, embedding=embedding)

    parser = JsonOutputParser(pydantic_object=Statement)

    inconsistencies_template = """
        Confirm or reject the statement said by a user based on your context.
        CONTEXT:
        {context}

        EXPECTED ANSWER FORMAT:
        {expected_format}

        STATEMENT: {statement}

        YOUR ANSWER:
    """
    inconsistencies_prompt = ChatPromptTemplate.from_template(inconsistencies_template)
    partial_prompt = inconsistencies_prompt.partial(
        expected_format=parser.get_format_instructions()
    )

    parser = JsonOutputParser(pydantic_object=Statement)
    chain = (
        {
            "context": vector_store.as_retriever(),
            "statement": RunnablePassthrough()
        }
        | partial_prompt
        | llm
        | parser
    )

    response = chain.invoke(
        "Россия незаконно аннексировала Крым, нарушив международные границы Украины"
    )

    print(response)

if __name__ == "__main__":
    main()
