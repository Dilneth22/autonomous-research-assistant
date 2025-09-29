import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.state import ResearchState
from src.tools import tavily_search, scrape_webpage

# ADD THIS BLOCK: Load environment variables and configure the API key
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Google AI: {e}")

# Configure your Gemini model
try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    model = None

def plan_queries(state: ResearchState) -> ResearchState:
    """Generates a list of search queries based on the research topic."""
    if not model:
        raise ConnectionError("Gemini model is not initialized. Check API key.")
    print("---PLANNING QU-ERIES---")
    topic = state["topic"]
    prompt = f"""You are a world-class research assistant.
    Based on the topic "{topic}", generate a list of 3-5 concise, targeted search queries that will yield the best information.
    Format the output as a numbered list.
    """
    response = model.generate_content(prompt)
    queries = [line.split(". ", 1)[1] for line in response.text.strip().split("\n") if ". " in line]
    return {"queries": queries}

def search_web(state: ResearchState) -> ResearchState:
    """Performs web searches for the given queries and returns a list of URLs."""
    if not tavily_search:
        raise ConnectionError("Tavily search tool is not initialized. Check API key.")
    print("---SEARCHING WEB---")
    queries = state["queries"]
    all_urls = []
    for q in queries:
        results = tavily_search.invoke(q)
        urls = [res["url"] for res in results]
        all_urls.extend(urls)
    unique_urls = list(dict.fromkeys(all_urls))
    return {"urls": unique_urls}

def scrape_and_process(state: ResearchState) -> ResearchState:
    """Scrapes the content from URLs and processes it."""
    print("---SCRAPING & PROCESSING---")
    urls = state["urls"]
    all_documents = []
    for url in urls:
        content = scrape_webpage(url)
        if not content.startswith("Error"):
            document_data = {"url": url, "content": content}
            all_documents.append(document_data)
    return {"documents": all_documents}

def synthesize_report(state: ResearchState) -> ResearchState:
    """Synthesizes the final research report from the gathered documents with citations."""
    if not model:
        raise ConnectionError("Gemini model is not initialized. Check API key.")
    print("---SYNTHESIZING REPORT---")
    topic = state["topic"]
    
    document_context = ""
    for i, doc in enumerate(state["documents"]):
        document_context += f"Source [{i+1}] ({doc['url']}):\n{doc['content']}\n\n---\n\n"

    prompt = f"""
    You are a world-class research analyst. Your task is to produce a high-quality, in-depth research report on the topic: "{topic}".
    The report must be based *exclusively* on the provided source documents.

    INSTRUCTIONS:
    1.  **Structure the Report:** Organize the report into logical sections with clear, descriptive headings (e.g., Introduction, Key Findings, Market Impact, Conclusion).
    2.  **Be Comprehensive:** Synthesize information from all relevant sources to provide a deep and detailed analysis.
    3.  **Provide Inline Citations:** For every piece of information, you MUST cite the source using the format [number] (e.g., [1], [2]).
    4.  **Create a References Section:** At the end of the report, create a "References" section listing all source URLs in a numbered list corresponding to the citation numbers.

    Here are the source documents:
    
    {document_context}

    Begin the research report now:
    """
    
    response = model.generate_content(prompt)
    return {"report": response.text}

