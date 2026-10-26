from langchain_core.messages import HumanMessage

from agent.agent import addmission_subgraph

ANSWER_NODES = {"generate_answer", "generate_query_or_respond"}

async def stream_agent(message: str, thread_id:str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        async for _, data in addmission_subgraph.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="messages",
            subgraphs=True
        ):
            message_chunk, metadata = data
            if metadata.get("langgraph_node") not in ANSWER_NODES:
                continue
            if message_chunk.content:
                yield message_chunk.content
    except Exception as e:
        yield f"\nError: {e}"
