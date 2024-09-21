from langchain_core.output_parsers import JsonOutputParser

def get_json_parser(pydantic_object):
    return JsonOutputParser(pydantic_object=pydantic_object)
