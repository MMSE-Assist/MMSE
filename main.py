import uuid

import streamlit as st
import logging
from langchain_core.messages import AIMessage, HumanMessage

from mmse_graph.mmse_construct_update.graph_mmse_only_update import create_mmse_graph

logging.basicConfig(level=logging.DEBUG)

@st.cache_resource
def get_graph():
    """Create the MMSE graph once and reuse it across all sessions."""
    return create_mmse_graph()


def main():
    st.title("MMSE Application")

    # Assign a stable thread ID per browser session for the Neo4j checkpointer
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Display messages list stores dicts with 'role' and 'content' for rendering
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Re-render previous messages on every rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your message…"):
        # Show and persist the user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        graph = get_graph()
        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                result = graph.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config=config,
                )

            # The last message in the returned state is the assistant reply
            ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
            response_text = ai_messages[-1].content if ai_messages else "*(no response)*"
            st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()

