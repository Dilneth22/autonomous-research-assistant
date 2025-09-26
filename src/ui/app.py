import sys
import os
import streamlit as st

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.graph.builder import build_graph

st.set_page_config(page_title="Autonomous Research Agent", layout="wide")
st.title("Autonomous Research Agent 🤖")

# --- Autonomous Research Section ---
st.header("Perform Autonomous Research")
topic_input = st.text_input(
    "Enter a topic to research:",
    placeholder="The impact of AI on the future of work"
)

if st.button("Start Research", key="start_research"):
    if topic_input:
        app = build_graph()
        inputs = {"topic": topic_input}
        
        with st.spinner("The research agent is working... This may take a few minutes."):
            final_report = ""
            # Stream the results to find the final report
            for output in app.stream(inputs, stream_mode="values"):
                if "report" in output and output["report"]:
                    final_report = output["report"]
            
            # Display the final report once the stream is complete
            if final_report:
                st.markdown("---")
                st.header("Research Report")
                st.markdown(final_report)
            else:
                st.error("The agent could not generate a report. Please try again.")
    else:
        st.warning("Please enter a research topic.")
