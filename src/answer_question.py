from .objects import llm
from .parsers.models import Statement
from .parsers import get_json_parser
from .objects import get_vector_store
from .prompts import get_inconcistencies_prompt
from .runnables import passthrough
import os

username = os.getenv("username")

def format_sections(sections):
    return "\n\n".join([d.page_content for d in sections])

def main():
    vector_store = get_vector_store(username=username)
    parser = get_json_parser(Statement)
    prompt = get_inconcistencies_prompt(parser)

    chain = (
        {"context": vector_store.as_retriever(), "statement": passthrough}
        | prompt
        | llm
        | parser
    )

    response = chain.invoke(
        "Volodymyr specializes in Java development"
    )

    print(response)

if __name__ == "__main__":
    main()
