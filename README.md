# Multi-Modal University Admission RAG Chatbot

An advanced, production-grade multi-modal Retrieval-Augmented Generation (RAG) chatbot designed for university admissions consultation. The system supports multi-modal interactions, allowing prospective students to query via text, upload academic records (transcript images), use voice input, and receive both text and synthetic speech responses.

## Architecture & Workflow

The core conversational engine is orchestrated using **LangGraph** and **LangChain**, implementing a sophisticated graph-based state machine that dynamically determines when to query external knowledge bases, grade retrieval relevance, and rewrite queries if necessary.

```
                  +---------------------------+
                  | generate_query_or_respond |
                  +---------------------------+
                    /                       \
          (Tool Call)                       (No Tool Call)
                   v                           v
             +----------+                     END
             | retrieve |
             +----------+
                   |
                   v
           +----------------+
           | grade_documents|
           +----------------+
              /          \
     (Relevant)            (Not Relevant)
          v                      v
 +------------------+   +-------------------+
 | generate_answer  |   | generate_new_query|
 +------------------+   +-------------------+
          |                      |
         END                     v
                         +------------------+
                         | retrieve_new_docs|
                         +------------------+
                                  |
                                  v
                         +----------------+
                         | grade_documents|
                         +----------------+
                            /          \
                   (Relevant)            (Retry limit reached /
                        v                  not relevant)
               +------------------+              v
               | generate_answer  |             END
               +------------------+
                        |
                       END
```

### Graph Execution Nodes & Conditional Routing
1. **`generate_query_or_respond`**:Acts as the entry point and decides whether the user's question requires knowledge-base retrieval. If a tool call is requested, the graph proceeds to **`retrieve`**; otherwise, the graph ends with the direct response.
2. **`retrieve` (Tool Node)**: Executes hybrid searches against the vector database when tool calls are triggered.
3. **`grade_documents`**: Assesses the relevance of retrieved documents to filter out noise. If documents are insufficient, routes to query rewriting.
4. **`generate_new_query`**: Rewrites and optimizes the retrieval query for subsequent search passes.
5. **`retrieve_new_docs`**: Searches Qdrant with the rewritten query, retrieves up to 10 documents, and stores the resulting context in the graph state before relevance grading.
6. **`generate_answer`**: Synthesizes the final response for the user based on verified context.

## Key Features

- **Multi-Modal Capabilities**: Supports image processing (e.g., transcript evaluation) via `qwen/qwen3-vl-32b-instruct` through OpenRouter API.
- **Voice Integration**: Speech-to-Text (STT) powered by `google/chirp-3` via OpenRouter API and Text-to-Speech (TTS) utilizing ElevenLabs (`eleven_flash_v2_5`).
- **Advanced Retrieval System**: Built on **Qdrant** vector database utilizing LLM-driven intelligent chunking, hybrid-search mechanisms, and top-$k=10$ document retrieval.
- **Robust State Management**: Powered by LangGraph's `StateGraph` and `MemorySaver` checkpointing for multi-turn conversation persistence.

## Performance Benchmarks

- **Standard Response (No Retrieval)**: ~2 - 4 seconds.
- **Complex Multi-Step Retrieval (With Query Rewriting & Document Grading)**: ~4 - 8 seconds.

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
├── chatbot_backend/
│   ├── agent/
│   │   ├── nodes/
│   │   │   ├── gen_query_or_response.py
│   │   │   ├── gen_answer.py
│   │   │   ├── grade_docs.py
│   │   │   ├── gen_new_query.py
│   │   │   └── tool_node.py
│   │   ├── agent.py
│   │   ├── helper.py
│   │   ├── prompts.py
│   │   └── state.py
│   ├── all_models/
│   │   ├── chat_llm.py
│   │   ├── openrouter_llm.py
│   │   └── vector_db.py
│   ├── service/
│   │   └── agent.py
│   ├── vector_database/
│   │   ├── create_add_documents.py
│   │   ├── create_db.py
│   │   └── documents_metadata.py
│   ├── main.py
│   └── voice.py
├── chatbot_mit_fe/
│   └── Chatbot_MIT/
│       └── my-app/
│           ├── app/
│           │   ├── components/
│           │   │   ├── Conversation.tsx
│           │   │   ├── Dialog.tsx
│           │   │   ├── PreviewImage.tsx
│           │   │   └── VoiceRecognite.tsx
│           │   ├── globals.css
│           │   ├── layout.tsx
│           │   └── page.tsx
│           ├── public/
│           ├── package.json
│           ├── next.config.ts
│           ├── postcss.config.mjs
│           └── tsconfig.json
├── .gitignore
└── README.md
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
