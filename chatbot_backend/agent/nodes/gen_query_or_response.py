from all_models.chat_llm import openai_llm as llm
from .tool_node import retrieve_document

from ..state import RecommendationState
from ..prompts import addmission_prompt

tools = [retrieve_document]

chain = (
    addmission_prompt
    | llm.bind_tools(tools)
)

def generate_query_or_respond(state: RecommendationState):
    recent_messages = state["messages"]
    response = chain.invoke({
        "messages": recent_messages
    })

    return {
        "messages": [response],
        "retry_count": 0,
        "retrieve_docs": "",
        "query_rewritten": "",
    }