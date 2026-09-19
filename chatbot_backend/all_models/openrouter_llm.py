import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openrouter_model_url = "https://openrouter.ai/api/v1"
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

openrouter_llm = OpenAI(
    base_url=openrouter_model_url,
    api_key= openrouter_api_key
)