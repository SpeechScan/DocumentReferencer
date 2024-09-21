import os
from langchain_openai import ChatOpenAI
from langchain_community.llms import OpenLLM

mode = os.environ.get("mode")
openai_api_key = os.environ.get("openai_api_key")
openai_model_name = os.environ.get("openai_model_name")

llm = (
    ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=openai_model_name,
        temperature=0.0,
    )
    if mode == "prod"
    else OpenLLM(
        model_name="dolly-v2",
        model_id="databricks/dolly-v2-3b",
        temperature=0.94,
        repetition_penalty=1.2,
    )
)
