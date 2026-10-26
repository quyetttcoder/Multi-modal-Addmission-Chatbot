from typing import Literal
from pydantic import BaseModel, Field

from ..helper import (
    get_last_human_message,
    get_last_tool_message,
)
from ..state import RecommendationState
from ..prompts import GRADE_PROMPT
from all_models.chat_llm import openai_llm as llm

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


grader_model = llm.with_structured_output(GradeDocuments)

def grade_documents(
    state: RecommendationState,
) -> Literal["generate_answer", "generate_new_query"]:


    human_message = get_last_human_message(
        state["messages"]
    )

    current_retry = state.get("retry_count", 0)

    if current_retry >= 1:
        return "generate_answer"

    tool_retrieve_docs = get_last_tool_message(
        state["messages"]
    )

    rewritten_retrieved_docs = state.get("retrieve_docs", "")

    if human_message is None or tool_retrieve_docs is None:
        return "generate_new_query"

    question = human_message.content
    context = tool_retrieve_docs.content
    if rewritten_retrieved_docs:
        context = rewritten_retrieved_docs

    prompt = GRADE_PROMPT.format(
        question=question,
        context=context
    )


    response = grader_model.invoke(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    if response.binary_score == "yes":
        return "generate_answer"
    return "generate_new_query"