from langchain.tools import tool
from all_models.vector_db import vector_store

@tool
def retrieve_document(query: str) -> str:
    """
    Use this tool when you need to search and retrieve information related to the university, majors, study programs, and admissions details.
    """
    results = vector_store.similarity_search(
        query,
        k=10,
    )

    docs = "\n\n".join(
        doc.page_content
        for doc in results
    )

    return docs