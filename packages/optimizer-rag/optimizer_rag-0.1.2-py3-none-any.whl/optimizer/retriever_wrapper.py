from langchain.schema import BaseRetriever
from typing import List
from .compressor import compress_chunk
from langchain.docstore.document import Document as LC_Document
from pydantic import PrivateAttr, Field

class ContextBudgetRetriever(BaseRetriever):
    _retriever: object = PrivateAttr()
    
    token_budget: int = Field(default=1000)

    def __init__(self, retriever, token_budget=1000, **kwargs):
        super().__init__(token_budget=token_budget, **kwargs)
        self._retriever = retriever

    def get_relevant_documents(self, query: str) -> List[LC_Document]:
        docs = self._retriever.get_relevant_documents(query)
        chunks = [doc.page_content for doc in docs]
        selected_chunks = compress_chunk(chunks, self.token_budget)
        output_docs = []
        for chunk in selected_chunks:
            meta = next((doc.metadata for doc in docs if doc.page_content == chunk), {})
            output_docs.append(LC_Document(page_content=chunk, metadata=meta))
        return output_docs
