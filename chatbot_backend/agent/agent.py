from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from .state import RecommendationState
from .nodes.gen_query_or_response import generate_query_or_respond
from .nodes.tool_node import retrieve_document
from .nodes.grade_docs import grade_documents
from .nodes.gen_new_query import gen_new_query, retrieve_new_docs
from .nodes.gen_answer  import generate_answer

tool_node = ToolNode([retrieve_document])


builder = StateGraph(RecommendationState)

builder.add_node("generate_query_or_respond", generate_query_or_respond)
builder.add_node("retrieve", tool_node)
builder.add_node("generate_answer", generate_answer)
builder.add_node("generate_new_query", gen_new_query)
builder.add_node("retrieve_new_docs", retrieve_new_docs)


builder.set_entry_point("generate_query_or_respond")

def route_on_tool_calls(state):
    latest_message = state["messages"][-1]

    if isinstance(latest_message, AIMessage) and latest_message.tool_calls:
        return "retrieve"

    return END


builder.add_conditional_edges(
    "generate_query_or_respond",
    route_on_tool_calls,
    {
        "retrieve": "retrieve",
        END: END,
    },
)

builder.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
    {
        "generate_answer": "generate_answer",
        "generate_new_query": "generate_new_query",
    }
)

builder.add_conditional_edges(
    "retrieve_new_docs",
    # Assess agent decision
    grade_documents,
    {
        "generate_answer": "generate_answer",
        "generate_new_query": "generate_new_query",
    }
)

builder.add_edge("generate_new_query", "retrieve_new_docs")
builder.add_edge("generate_answer", END)

addmission_subgraph = builder.compile(checkpointer=MemorySaver())