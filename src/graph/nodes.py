import os
import google.generativeai as genai
from dotenv import load_dotenv

from src.state import ResearchState
from src.tools import tavily_search, scrape_webpage
from src.vectorstore import create_vector_store, query_vector_store

# Load and configure APIs
load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found.")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"Error configuring Google Gemini: {e}")
    model = None

# --- AGENTS FOR INITIAL RESEARCH PHASE ---

def plan_queries(state: ResearchState) -> ResearchState:
    """Generates a list of search queries based on the research topic."""
    print("---PLANNING QUERIES---")
    if not model: raise ConnectionError("Model not configured.")
    topic = state["topic"]
    prompt = f"""You are a world-class research assistant. Based on the topic "{topic}", generate a list of 3-5 concise, targeted search queries."""
    response = model.generate_content(prompt)
    # Basic parsing of a numbered list
    queries = [line.split(". ", 1)[1] for line in response.text.strip().split("\n") if ". " in line]
    return {"queries": queries}

def search_web(state: ResearchState) -> ResearchState:
    """Performs web searches for the given queries and returns a list of URLs."""
    print("---SEARCHING WEB---")
    if not tavily_search: raise ConnectionError("Tavily Tool not configured.")
    queries = state["queries"]
    all_urls = []
    for q in queries:
        results = tavily_search.invoke(q)
        urls = [res["url"] for res in results]
        all_urls.extend(urls)
    unique_urls = list(dict.fromkeys(all_urls))
    return {"urls": unique_urls}

def scrape_and_process(state: ResearchState) -> ResearchState:
    """Scrapes the content from URLs, skipping non-HTML files."""
    print("---SCRAPING & PROCESSING---")
    urls = state["urls"]
    all_documents = []
    for url in urls:
        if url.endswith((".pdf", ".docx", ".zip", ".pptx", ".xlsx")):
            print(f"--> Skipping non-HTML file: {url}")
            continue
        content = scrape_webpage(url)
        if not content.startswith("Error"):
            all_documents.append({"url": url, "content": content})
    return {"documents": all_documents}

# --- NEW AGENT FOR BUILDING THE VECTOR DATABASE ---

def ingest_and_embed(state: ResearchState) -> ResearchState:
    """Takes scraped documents, creates a vector store, and saves its path."""
    if not state["documents"]:
        print("---No documents to ingest. Skipping vector store creation.---")
        return {"topic_index_path": ""}
    index_path = create_vector_store(state["topic"], state["documents"])
    return {"topic_index_path": index_path}

def synthesize_initial_report(state: ResearchState) -> ResearchState:
    """Generates the initial full report based on the newly created vector store."""
    print("---SYNTHESIZING INITIAL REPORT---")
    if not model: raise ConnectionError("Model not configured.")
    topic = state["topic"]
    if not state["topic_index_path"]:
        return {"report": "Could not generate a report because no documents were successfully scraped and indexed."}
        
    # Query the vector store for a broad context on the main topic
    context_docs = query_vector_store(topic, state["topic_index_path"])
    context_str = "\n\n---\n\n".join([f"Source ({doc.metadata['source']}):\n{doc.page_content}" for doc in context_docs])
    
    prompt = f"""You are a professional research analyst. Based on the following documents, write a detailed and comprehensive research report on the topic: "{topic}".
    The report should be well-structured, easy to read, and cover the key aspects of the topic based on the provided context.
    
    Documents:
    {context_str}
    
    Research Report:
    """
    response = model.generate_content(prompt)
    return {"report": response.text}

# --- NEW AGENT FOR THE Q&A PHASE ---

def answer_follow_up_question(state: ResearchState) -> ResearchState:
    """Answers a specific follow-up question using the topic's vector store."""
    print("---ANSWERING FOLLOW-UP QUESTION---")
    if not model: raise ConnectionError("Model not configured.")
    question = state["follow_up_question"]
    
    # Retrieve context relevant to the specific question
    context_docs = query_vector_store(question, state["topic_index_path"])
    context_str = "\n\n---\n\n".join([f"Source ({doc.metadata['source']}):\n{doc.page_content}" for doc in context_docs])

    prompt = f"""Based *only* on the provided documents, give a direct and concise answer to the following question: "{question}"
    
    If the answer is not found in the documents, state that you cannot find the information based on the provided context. When possible, cite your sources using the format [Source URL].
    
    Documents:
    {context_str}
    
    Answer:
    """
    response = model.generate_content(prompt)
    return {"follow_up_answer": response.text}

