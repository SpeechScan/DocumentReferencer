from src.objects import get_vector_store
import os 


store = get_vector_store(os.getenv('username'))
retriever = store.as_retriever()
docs = retriever.invoke("Россия")

print(docs)
