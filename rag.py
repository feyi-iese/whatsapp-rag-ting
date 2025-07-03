# rag.py
import os
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv; load_dotenv()

emb = OpenAIEmbeddings(model="text-embedding-3-small")
client = QdrantClient(
    url=os.getenv("QDRANT_URL"), prefer_grpc=True
)

store = Qdrant(
    client=client,
    collection_name=os.getenv("COLLECTION"),
    embeddings=emb,
)

retriever = store.as_retriever(search_kwargs={"k":4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def get_answer(question: str) -> str:
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)
    system = (
        "You are Ting CRM Assistant. "
        "Answer strictly from the context. If unsure, say you don't know."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": f"Context:\n{context}"},
        {"role": "user", "content": question},
    ]
    resp = llm.invoke(messages)
    return resp.content