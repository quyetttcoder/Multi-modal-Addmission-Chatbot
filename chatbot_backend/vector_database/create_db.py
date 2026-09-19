import os
from dotenv import load_dotenv
from langchain_qdrant import FastEmbedSparse
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams

load_dotenv(override=True)

qdrant_url = os.environ.get("QDRANT_URL")
qdrant_key = os.environ.get("QDRANT_API_KEY")

SPARSE_EMBEDDING = "Qdrant/bm25"

sparse_model = FastEmbedSparse(model_name=SPARSE_EMBEDDING)

# Create a Qdrant client for local storage
client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_key
)

# Create a collection with both dense and sparse vectors
client.create_collection(
    collection_name="MIT_Chatbot_KB",
    vectors_config={"dense": VectorParams(size=1024, distance=Distance.COSINE)},
    sparse_vectors_config={
        "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
    },
)