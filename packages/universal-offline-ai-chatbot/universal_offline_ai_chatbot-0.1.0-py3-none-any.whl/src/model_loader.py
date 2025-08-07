# === src/model_loader.py ===
from langchain_community.chat_models import ChatOllama

def load_llm():
    return ChatOllama(model="mistral:instruct", temperature=0.5)