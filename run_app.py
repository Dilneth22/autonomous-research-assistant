import streamlit as st
from src.graph.builder import build_graph

st.set_page_config(page_title="Autonomous Research Agent", layout="wide")
st.title("Autonomous Research Agent 🤖")

# Research Input Section
topic = st.text_input(
    "Enter a topic to research:",
    placeholder="The impact of AI on healthcare"
)

if st.button("Start Research", key="start_research"):
    if topic:
        try:
            with st.spinner("Building research workflow..."):
                app = build_graph()
            
            with st.spinner("Conducting research... This may take a few minutes."):
                # Initialize state with the topic
                inputs = {"topic": topic}
                
                # Create a placeholder for the report
                report_placeholder = st.empty()
                
                # Stream the results
                for output in app.stream(inputs):
                    if "report" in output and output["report"]:
                        report_placeholder.markdown(output["report"])
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a research topic.")