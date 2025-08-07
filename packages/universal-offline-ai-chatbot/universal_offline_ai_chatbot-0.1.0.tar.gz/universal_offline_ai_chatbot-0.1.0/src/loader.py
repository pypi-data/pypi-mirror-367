# === src/loader.py ===
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

def load_pdf_files(data_path):
    loader = DirectoryLoader(data_path, glob='*.pdf', loader_cls=PyPDFLoader)
    return loader.load()