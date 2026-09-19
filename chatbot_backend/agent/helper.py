from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

def get_last_human_message(messages):
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message

    return None

def get_last_tool_message(messages):
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            return message

    return None

def format_chat_history(messages):
    history = []

    for message in messages:
        if isinstance(message, HumanMessage):
            history.append(
                f"Người dùng: {message.content}"
            )
        elif isinstance(message, AIMessage):
            history.append(
                f"Trợ lý: {message.content}"
            )

    return "\n".join(history)