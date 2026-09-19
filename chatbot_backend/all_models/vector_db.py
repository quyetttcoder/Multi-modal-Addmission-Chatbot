import os
from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from langchain_qdrant import QdrantVectorStore

load_dotenv()

MODEL_NAME = "BAAI/bge-m3"
SPARSE_EMBEDDING = "Qdrant/bm25"

qdrant_url = os.environ.get("QDRANT_URL")
qdrant_key = os.environ.get("QDRANT_API_KEY")

embedding_model = HuggingFaceEmbeddings(
    model = MODEL_NAME,
    model_kwargs = {"device": "cpu"}, # "device": "cuda" for emvedding and "cpu" for retrive if not enough VRAM
    encode_kwargs = {"normalize_embeddings": True}
)

sparse_embeddings = FastEmbedSparse(model_name=SPARSE_EMBEDDING)

vector_store = QdrantVectorStore.from_existing_collection(
    collection_name="MIT_Chatbot_KB",
    embedding=embedding_model,
    sparse_embedding=sparse_embeddings,
    url=qdrant_url,
    prefer_grpc=True,
    api_key=qdrant_key,
    vector_name="dense",
    sparse_vector_name="sparse",
    retrieval_mode=RetrievalMode.HYBRID
)