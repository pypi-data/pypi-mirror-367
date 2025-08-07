# === src/chunker.py ===
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documents)