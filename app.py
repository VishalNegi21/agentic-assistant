import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage

from backend import workflow
import uuid

# unique thread id for each session
def generate_thread_id():
    return str(uuid.uuid4())

# add a unique thread id to the session state if it doesn't exist
def add_thread_id(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

# reset the chat by clearing the messages and generating a new thread id
def reset_chat():
    # generate new thread id
    st.session_state["thread_id"] = generate_thread_id()

    # clear messages of current chat
    st.session_state["messages"] = []

    # add the new thread id to the list of chat threads
    add_thread_id(st.session_state["thread_id"])

def load_messages(thread_id):
    # get the saved state for the given thread id from the workflow
    state = workflow.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    # return the messages from the state, or an empty list if there are no messages
    return state.values.get("chats", [])

    

st.set_page_config(page_title="Agentic Chatbot", page_icon="💬")
st.title("Agentic Chatbot")
st.caption("Ask a question and get a response from the LangGraph workflow.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# create thread id for when app runs for first time 
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()
    

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = {}

#add currnt threads to the list of chat threads
add_thread_id(st.session_state["thread_id"])


# -------------------------add a simple sidebar to select a thread id or create a new one------------------------------
st.sidebar.title("Chat Threads")
if st.sidebar.button("New Chat"):

    # reset chat and create new thread
    reset_chat()

    # rerun to update interface
    st.rerun()

# display the list of chat threads in reverse order (most recent first)
for thread_id in st.session_state["chat_threads"][::-1]:
    # Look up the title, default to "New Chat" if it's empty
    chat_title = st.session_state["thread_titles"].get(thread_id, thread_id)

    if st.sidebar.button(
        str(chat_title),
        key=thread_id
    ):
        # set the current thread id to the selected one
        st.session_state["thread_id"] = thread_id

        # load the messages for the selected thread id
        messages= load_messages(thread_id)

        # list for convert
        temporary_messages = []

        # loop through the messages and convert them to the format expected by the chat interface
        for message in messages:
            # LangChain messages are objects, so we check the '.type' attribute
            if message.type == "human":
                temporary_messages.append(
                    {"role": "user", "content": message.content}
                )
            elif message.type == "ai":
                temporary_messages.append(
                    {"role": "assistant", "content": message.content}
                )
            else:
                continue
        # set the session state messages to the converted messages
        st.session_state["messages"] = temporary_messages

        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# input 
if prompt := st.chat_input("Send a message"):

    # If this thread doesn't have a title yet, generate one from the prompt
    if st.session_state.thread_id not in st.session_state["thread_titles"]:
        # Grab first 25 chars and add "..."
        st.session_state["thread_titles"][st.session_state.thread_id] = prompt[:25] + "..."

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # display the user message in the chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # configure the LangGraph workflow with the current thread id
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # answer the user message using the LangGraph workflow and stream the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # st.write_stream renders the text to the UI automatically
                # and saves the final output to the 'response' variable
                response = st.write_stream(
                    chunk.content for chunk,metadata in workflow.stream(
                        {"chats": [HumanMessage(content=prompt)]},
                        config=config,
                        # stream_mode='messages' is required to stream the response as messages
                        stream_mode="messages",
                    )
                    # only include the content of the AIMessage chunks in the response
                    if isinstance(chunk, AIMessage)
                )
            except Exception as error:
                response = f"I could not process that message: {error}"

        
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

