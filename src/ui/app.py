import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now import the required modules
import streamlit as st
from src.orchestrator import run_digest, process_single_url
from src.config import load_settings

st.set_page_config(page_title="Autonomous Research Assistant", layout="wide")

st.title("Autonomous Research Assistant 🤖")

# --- Section for Adding New URLs ---
st.header("Add New Sources")

# CHANGED: Use a text area for multiple URLs
url_input = st.text_area(
    "Enter URLs to add (one per line):",
    placeholder="https://example.com/article-1\nhttps://example.com/article-2",
    height=150
)

if st.button("Process URLs", key="process_urls"):
    # CHANGED: Split the input into a list of URLs and filter out empty lines
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    
    if urls:
        st.info(f"Found {len(urls)} URLs to process. Starting...")
        # CHANGED: Loop through each URL and process it
        for url in urls:
            try:
                with st.spinner(f"Processing: {url}..."):
                    result_message = process_single_url(url)
                st.success(result_message, icon="✅")
            except Exception as e:
                st.error(f"Failed to process {url}: {e}", icon="❌")
        st.success("All URLs have been processed!")
    else:
        st.warning("Please enter at least one URL.")

st.markdown("---")

# --- Section for Creating Research Digest ---
st.header("Create a Research Digest")
settings = load_settings()
default_topics = ", ".join(settings.topics)

topic_input = st.text_area(
    "Enter topics to research (comma-separated):",
    value=default_topics,
    height=100
)

if st.button("Generate Digest", key="generate_digest"):
    if topic_input:
        topics = [topic.strip() for topic in topic_input.split(',')]
        with st.spinner("Generating your research digest... This may take a moment."):
            try:
                digest_output = run_digest(topics)
                st.markdown(digest_output)
            except Exception as e:
                st.error(f"An error occurred while generating the digest: {e}")
    else:
        st.warning("Please enter at least one topic.")