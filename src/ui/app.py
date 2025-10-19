import sys
import os
import streamlit as st

# Add project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.graph.builder import build_research_graph
from src.graph.nodes import answer_follow_up_question

st.set_page_config(page_title="Hybrid RAG Agent", layout="wide")
st.title("Hybrid Autonomous RAG Agent 🧠")

# Initialize session state variables to manage the app's flow
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False
    st.session_state.full_report = ""
    st.session_state.index_path = ""
    st.session_state.topic = ""
    st.session_state.messages = []

# --- PHASE 1: AUTONOMOUS RESEARCH ---
# This section runs if the initial research has not been completed yet.
if not st.session_state.research_complete:
    st.header("1. Start a New Research Task")
    topic_input = st.text_input(
        "Enter a topic for the agent to research:",
        placeholder="e.g., The future of renewable energy in South Asia"
    )

    if st.button("Start Research", key="start_research"):
        if topic_input:
            st.session_state.topic = topic_input
            st.session_state.messages = []  # Clear chat from previous sessions
            research_graph = build_research_graph()
            inputs = {"topic": topic_input}
            
            with st.spinner("Autonomous agent is working... This may take a few minutes."):
                final_state = {}
                # Stream the output of the graph to get the final state
                for output in research_graph.stream(inputs, stream_mode="values"):
                    final_state.update(output)

                # Store the results in the session state
                st.session_state.full_report = final_state.get("report", "No report could be generated.")
                st.session_state.index_path = final_state.get("topic_index_path", "")
                st.session_state.research_complete = True
                st.rerun()  # Rerun the script to switch to the Q&A phase
        else:
            st.warning("Please enter a research topic.")

# --- PHASE 2: INTERACTIVE Q&A ---
# This section runs after the initial research is complete.
else:
    st.header(f"2. Ask Follow-up Questions on: {st.session_state.topic}")
    
    # Display the full report in a collapsible section
    with st.expander("View Full Initial Report", expanded=False):
        st.markdown(st.session_state.full_report)

    # Display the chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle new chat input
    if prompt := st.chat_input("Ask a specific question about the research..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.spinner("Searching the knowledge base..."):
            # Prepare the state needed for the Q&A agent
            qa_state = {
                "follow_up_question": prompt,
                "topic_index_path": st.session_state.index_path
            }
            # Call the Q&A agent directly
            result_state = answer_follow_up_question(qa_state)
            answer = result_state.get("follow_up_answer", "Sorry, I couldn't find an answer in the provided context.")
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)
    
    # Button to reset the app and start a new research topic
    if st.button("Start New Research Topic"):
        # Clear all session state keys to reset the app
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

