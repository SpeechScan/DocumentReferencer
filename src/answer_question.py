from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
import os

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

    # Initialize a LangChain object for retrieving information from Pinecone.
    knowledge = PineconeVectorStore.from_existing_index(
        index_name=pinecone_index,
        namespace=username,
        embedding=PineconeEmbeddings(
            model=pinecone_embedding_model, pinecone_api_key=pinecone_api_key
        ),
    )

    # Initialize a LangChain object for chatting with the LLM
    # with knowledge from Pinecone.
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=knowledge.as_retriever()
    )

    query = "На каких принципах основывается база?"
    print(qa.invoke(query).get("result"))

if __name__ == "__main__":
    main()
