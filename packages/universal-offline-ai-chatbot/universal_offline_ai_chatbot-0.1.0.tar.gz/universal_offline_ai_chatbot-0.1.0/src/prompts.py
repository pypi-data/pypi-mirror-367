# src/prompts.py

from langchain_core.prompts import PromptTemplate

CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, say you don't know — do not make it up.
Only refer to the context provided.

Context: {context}
Question: {question}

Start the answer directly without unnecessary text.
"""

def set_custom_prompt(template: str = CUSTOM_PROMPT_TEMPLATE) -> PromptTemplate:
    return PromptTemplate(template=template, input_variables=["context", "question"])
