import base64
from typing import List
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage

from chatbot_backend.all_models.openrouter_llm import openrouter_llm as client
from chatbot_backend.agent.agent import addmission_subgraph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VISION_PROMPT = """
You are an advanced document analysis system. Your task is to extract complete information from the provided document.

Strict Requirements:
1. Extract all information comprehensively and accurately without omission.
2. Format the output entirely in Markdown.
3. Output ONLY the extracted information from the document; do NOT include any explanations, introductions, or conversational filler.
"""

config = {"configurable": {"thread_id": "1"}}



def get_agent_response_string(message: str) -> str:
    output = addmission_subgraph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    chatbot_response = next(
        (
            msg
            for msg in reversed(output["messages"])
            if isinstance(msg, AIMessage)
        ),
        None,
    )

    return (
        chatbot_response.content
        if chatbot_response
        else "No response from the AI."
    )


async def build_vision_content(files: List[UploadFile]):
    content = [{"type": "text", "text": VISION_PROMPT}]

    for file in files:
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{file.content_type};base64,{base64_image}"
                },
            }
        )

    return content


@app.post("/chat")
async def main(
    message: str = Form(...),
    files: List[UploadFile] = File([]),
):
    if files:
        content = await build_vision_content(files)

        response = client.chat.completions.create(
            model="qwen/qwen3-vl-32b-instruct",
            temperature=0,
            messages=[{"role": "user", "content": content}],
        )

        if response.choices:
            ocr_text = response.choices[0].message.content
            extra_prompt = (
                f"\n\n====================\n"
                f"Document content:\n\n{ocr_text}"
            )
            message += extra_prompt

    response_text = get_agent_response_string(message)

    return {"reply": response_text}

if __name__ == "__main__":
    uvicorn.run(
        "chatbot_backend.main:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
    )
