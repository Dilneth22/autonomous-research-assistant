import streamlit as st
from ..agents.retrieval_agent import retrieve
from ..orchestrator import run_digest

st.set_page_config(page_title="Research Assistant", layout="wide")

st.title("Autonomous Research Assistant")
tab1, tab2 = st.tabs(["Search", "Daily Digest"])

with tab1:
    q = st.text_input("Query", "AI in healthcare")
    k = st.slider("Top K", 1, 20, 8)
    if st.button("Search"):
        res = retrieve(q, k)
        for r in res:
            st.write(f"**{r.get('title','(untitled)')}** - {r.get('url','')}")
            st.write(r.get("text","")[:500] + "...")
            st.caption(f"Distance: {r.get('_distance','?')}")

with tab2:
    if st.button("Generate Digest"):
        digest = run_digest()
        st.markdown(digest)
