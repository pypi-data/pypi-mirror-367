# === src/config.py ===
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

HF_TOKEN = os.environ.get("HF_TOKEN")
DATA_PATH = "data/"
DB_FAISS_PATH = "vectorstore/db_faiss"
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, say you don't know — do not make it up.
Only refer to the context provided.

Context: {context}
Question: {question}

Start the answer directly without unnecessary text.
"""