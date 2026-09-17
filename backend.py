from langgraph.graph import StateGraph , START , END, add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)




class State(TypedDict):
    chats : Annotated[list[BaseMessage] , add_messages]



def chat(state: State):
    # take question from state and send it to the LLM
    messages = state["chats"]
    res = llm.invoke(messages)

    # add the response to the state
    return {
        'chats':[res]
    }


checkpoint = MemorySaver()
graph = StateGraph(State)

graph.add_node('chat' , chat)

graph.add_edge(START , 'chat')
graph.add_edge('chat' , END)

workflow = graph.compile(checkpointer=checkpoint)