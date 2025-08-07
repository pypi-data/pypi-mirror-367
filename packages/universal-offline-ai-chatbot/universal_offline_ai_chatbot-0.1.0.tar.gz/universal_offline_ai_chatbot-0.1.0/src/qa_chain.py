# === src/qa_chain.py ===
from langchain.chains import RetrievalQA

def setup_qa_chain(llm, db, prompt):
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
