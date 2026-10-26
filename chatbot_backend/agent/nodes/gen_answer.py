from langchain_core.messages import AIMessage
from ..state import RecommendationState
from ..prompts import GENERATE_PROMPT
from ..helper import get_last_human_message, get_last_tool_message
from all_models.chat_llm import openai_llm as llm


async def generate_answer(state: RecommendationState):

    messages = state["messages"]

    question = get_last_human_message(
        messages
    ).content

    rewritten_retrieved_docs = state.get("retrieve_docs", "")

    tool_message = get_last_tool_message(
        messages
    )

    if tool_message is None:
        context = ""
    elif rewritten_retrieved_docs:
        context = rewritten_retrieved_docs
    else:
        context = tool_message.content

    prompt = GENERATE_PROMPT.format(
        question=question,
        context=context
    )

    content = llm.invoke(prompt).content

    return {
        "messages": [
            AIMessage(content=content)
        ]
    }