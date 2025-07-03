import os, glob, time
from dotenv import load_dotenv; load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.documents import Document

# ----- config --------------------------------------------------------------
COLLECTION = os.getenv("COLLECTION", "ting_docs")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# ----- load + chunk --------------------------------------------------------
def load_docs(folder="data"):
    for path in glob.glob(f"{folder}/**/*.*", recursive=True):
        with open(path, encoding="utf-8") as f:
            yield f.read(), path

docs = []
for text, src in load_docs():
    for chunk in splitter.split_text(text):
        docs.append(Document(page_content=chunk, metadata={"source": src}))

# ----- embed + upsert ------------------------------------------------------
print(f"Embedding {len(docs)} chunks …")
t0 = time.time()

Qdrant.from_documents(
    documents=docs,
    embedding=embedder,
    url=QDRANT_URL,
    prefer_grpc=True,
    collection_name=COLLECTION,
    force_recreate=True,
)

print(f"✓ done in {time.time() - t0:.1f}s")