# === src/vectorstore.py ===
import os
from langchain_community.vectorstores import FAISS

def build_vector_db(chunks, embedding_model, db_path):
    db = FAISS.from_documents(chunks, embedding_model)
    db.save_local(db_path)

def load_vector_db(db_path, embedding_model):
    return FAISS.load_local(db_path, embedding_model, allow_dangerous_deserialization=True)