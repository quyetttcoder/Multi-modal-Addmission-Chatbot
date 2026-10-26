from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_model = "gpt-4o-mini"
qwen35_model = "qwen/qwen3.5-35b-a3b"

openrouter_model_url = "https://openrouter.ai/api/v1"
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

openai_key = os.environ.get("OPENAI_API_KEY")

openai_llm = ChatOpenAI(
    model=openai_model, 
    api_key=openai_key,
    streaming=True,
    temperature=0
)
