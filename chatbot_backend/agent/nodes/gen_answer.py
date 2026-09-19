from langchain_core.messages import AIMessage
from ..state import RecommendationState
from ..prompts import GENERATE_PROMPT
from ..helper import get_last_human_message, get_last_tool_message
from chatbot_backend.all_models.chat_llm import qwen35_model as llm


def generate_answer(state: RecommendationState):

    messages = state["messages"]

    question = get_last_human_message(
        messages
    ).content

    tool_message = get_last_tool_message(
        messages
    )

    if tool_message is None:
        context = ""
    else:
        context = tool_message.content

    print("===CONTEXT FOR GEN ANSWER====")
    print(context)
    print("================")

    prompt = GENERATE_PROMPT.format(
        question=question,
        context=context
    )

    response = llm.invoke(prompt)

    return {
        "messages": [
            AIMessage(content=response.content)
        ]
    }