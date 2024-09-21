from .objects import llm
from .objects import get_vector_store
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import os

username = os.getenv("username")

class Statement(BaseModel):
    statement: str = Field(description="A statement said by a person")
    isStatementTrue: bool = Field(description="Can statement be confirmed by your knowledge?")
    rejectionReasons: List[str] = Field(description="Array of sections from your knowledge based on which you rejected the statement. If statement is not false and can be confirmed by your knowledge, then make this array empty.")

def format_sections(sections):
    return "\n\n".join([d.page_content for d in sections])

def main():
    vector_store = get_vector_store(username=username)
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
