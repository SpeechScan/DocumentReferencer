from langchain_core.prompts import ChatPromptTemplate

def get_inconcistencies_prompt(json_parser):
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
        expected_format=json_parser.get_format_instructions()
    )
    return partial_prompt
