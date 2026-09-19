from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import get_buffer_string, AIMessage
import uuid

from chatbot_backend.all_models.chat_llm import openai_llm as llm
from chatbot_backend.all_models.vector_db import vector_store

from ..state import RecommendationState
from ..prompts import GENERATE_SEMANTIC_QUERY
from ..helper import get_last_human_message


multi_query_gen_prompt = ChatPromptTemplate.from_template(GENERATE_SEMANTIC_QUERY)

retriever = vector_store.as_retriever(search_kwargs={"k":10})

chain = multi_query_gen_prompt | llm

def gen_new_query(state: RecommendationState):
    messages = state["messages"]
    current_retry = state.get("retry_count", 0)

    latest_user_query = get_last_human_message(messages)
    history_messages = messages[:-1] if len(messages) > 1 else []
    chat_history_str = (
        get_buffer_string(history_messages)
        if history_messages
        else "Empty conversation."
    )

    output = chain.invoke(
        {"chat_history": chat_history_str, "question": latest_user_query}
    )

    print("======= GEN NEW QUERY ======")
    print("Generated Query/Tags: ", output.content)
    print("=============================")

    tool_call_id = str(uuid.uuid4())
    
    ai_message_with_tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "retrieve_document", 
                "args": {"query": output.content},
                "id": tool_call_id
            }
        ]
    )

    return {
        "messages": [ai_message_with_tool_call],
        "retry_count": current_retry + 1
    }
