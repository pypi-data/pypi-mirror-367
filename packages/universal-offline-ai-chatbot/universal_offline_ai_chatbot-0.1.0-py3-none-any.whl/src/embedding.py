# === src/embedding.py ===
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

def get_embedding_model():
    load_dotenv()  # load from .env
    hf_token = os.getenv("HF_TOKEN")

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"use_auth_token": hf_token}
    )
