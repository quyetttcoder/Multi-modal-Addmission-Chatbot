# Multi-Modal University Admission RAG Chatbot

An advanced, production-grade multi-modal Retrieval-Augmented Generation (RAG) chatbot designed for university admissions consultation. The system supports multi-modal interactions—allowing prospective students to query via text, upload academic records (transcript images), use voice input, and receive both text and synthetic speech responses.

## Architecture & Workflow

The core conversational engine is orchestrated using **LangGraph** and **LangChain**, implementing a sophisticated graph-based state machine that dynamically determines when to query external knowledge bases, grade retrieval relevance, and rewrite queries if necessary.

```
                  +---------------------------+
                  | generate_query_or_respond |
                  +---------------------------+
                    /                       \
        (Tool Call) /                         \ (No Tool Call)
                   v                           v
             +----------+                     END
             | retrieve |
             +----------+
                   |
     (Grade Docs)  v
         +------------------+
         | grade_documents  |
         +------------------+
           /              \
(Relevant) /                \ (Not Relevant / Rewrite)
          v                  v
+------------------+  +-------------------+
|  generate_answer |  | generate_new_query|
+------------------+  +-------------------+
         |                    |
        END                   v
                   +-------------------+
                   |     retrieve      |
                   +-------------------+
```

### Graph Execution Nodes & Conditional Routing
1. **`generate_query_or_respond`**: Acts as the entry point and primary agent decision-maker. It evaluates user input and decides whether external retrieval tools are necessary.
2. **`retrieve` (Tool Node)**: Executes hybrid searches against the vector database when tool calls are triggered.
3. **`grade_documents`**: Assesses the relevance of retrieved documents to filter out noise. If documents are insufficient, routes to query rewriting.
4. **`generate_new_query`**: Rewrites and optimizes the retrieval query for subsequent search passes.
5. **`generate_answer`**: Synthesizes the final response for the user based on verified context.

## Key Features

- **Multi-Modal Capabilities**: Supports image processing (e.g., transcript evaluation) via `qwen/qwen3-vl-32b-instruct` through OpenRouter API.
- **Voice Integration**: Speech-to-Text (STT) powered by `google/chirp-3` via OpenRouter API and Text-to-Speech (TTS) utilizing ElevenLabs (`eleven_flash_v2_5`).
- **Advanced Retrieval System**: Built on **Qdrant** vector database utilizing LLM-driven intelligent chunking, hybrid-search mechanisms, and top-$k=10$ document retrieval.
- **Robust State Management**: Powered by LangGraph's `StateGraph` and `MemorySaver` checkpointing for multi-turn conversation persistence.

## Performance Benchmarks

- **Standard Response (No Retrieval)**: ~5 - 10 seconds.
- **Complex Multi-Step Retrieval (With Query Rewriting & Document Grading)**: ~25 - 40 seconds.

## Tech Stack

- **Orchestration**: LangChain, LangGraph
- **Vector Database**: Qdrant
- **Backend**: FastAPI, Python
- **Frontend**: Next.js, TypeScript
- **APIs & Models**: 
  - Vision Model: `qwen/qwen3-vl-32b-instruct` (via OpenRouter)
  - STT Model: `google/chirp-3` (via OpenRouter)
  - TTS Model: `eleven_flash_v2_5` (ElevenLabs)

## Project Structure

```text
├── backend/
│   ├── agent/
│   │   ├── nodes/
│   │   │   ├── gen_query_or_response.py
│   │   │   ├── gen_answer.py
│   │   │   ├── grade_docs.py
│   │   │   ├── gen_new_query.py
│   │   │   └── tool_node.py
│   │   ├── state.py
|   |   ├── agent.py
|   |   ├── prompts.py
│   │   └── helper.py
│   ├── all_models/
│   │   ├── chat_llm.py
│   │   ├── openrouter_llm.py
│   │   ├── vector_db.py
│   ├── vector_database/
│   │   ├── documents/
│   │   ├── create_add_documents.py
│   │   ├── create_db.py
│   │   ├── documents_metadata.py
│   └── main.py
│   └── voice.py
└── frontend/
    └── src/
        ├── components/
        └── app/
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Qdrant instance
- API Keys: OpenRouter API Key, ElevenLabs API Key

### Backend Setup

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Configure environment variables in a `.env` file:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```
4. Run the FastAPI server:
   ```bash
   python -m chatbot_backend.main
   ```
5. Run the Voice:
   ```bash
   python -m chatbot_backend.voice
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd .\chatbot_mit_fe\Chatbot_MIT\my-app\
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev