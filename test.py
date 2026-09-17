from backend import workflow
from langchain_core.messages import BaseMessage, HumanMessage

for chunk , metadata in workflow.stream(
    {"chats": [HumanMessage(content="Write an essay about the benefits of exercise.")]},
    config={"configurable": {"thread_id": "test-thread"}},
    stream_mode="messages",
):
    print(chunk.content,end="",flush=True) 