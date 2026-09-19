from typing_extensions import TypedDict, List, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class RecommendationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    query_rewritten: str
    rewrite_status: bool
    retrieve_docs: str
    retry_count: int