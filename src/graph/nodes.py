import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from src.state import ResearchState
from src.tools import tavily_search, scrape_webpage

# Load environment variables from .env file
load_dotenv()

# --- Configure the Google API Key ---
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # CHANGED: Use a model name confirmed to be available for your API key
    model = genai.GenerativeModel("models/gemini-pro-latest")

except Exception as e:
    print(f"Error configuring Google Gemini: {e}")
    model = None

def plan_queries(state: ResearchState) -> ResearchState:
    """Generates a list of search queries based on the research topic."""
    if not model:
        raise ConnectionError("Google Gemini model is not configured. Please check your API key.")
    
    print("---PLANNING QUERIES---")
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
        raise ConnectionError("Tavily Search Tool is not configured. Please check your API key.")

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
    return {"documents": alldocuments}

def summarize_documents_individually(state: ResearchState) -> ResearchState:
    """Summarizes each scraped document one by one to avoid rate limits."""
    if not model:
        raise ConnectionError("Google Gemini model is not configured. Please check your API key.")

    print("---SUMMARIZING INDIVIDUAL DOCUMENTS---")
    summaries = []
    for doc in state["documents"]:
        prompt = f"""Based on the following document, please provide a concise but comprehensive summary.
        
        Document Content:
        {doc['content']}
        """
        try:
            response = model.generate_content(prompt)
            summaries.append({"url": doc["url"], "summary": response.text})
            # Wait for a second to respect rate limits
            time.sleep(1) 
        except Exception as e:
            print(f"Error summarizing document {doc['url']}: {e}")
            continue
            
    return {"individual_summaries": summaries}

def synthesize_report(state: ResearchState) -> ResearchState:
    """Synthesizes the final research report from the individual summaries."""
    if not model:
        raise ConnectionError("Google Gemini model is not configured. Please check your API key.")
        
    print("---SYNTHESIZING FINAL REPORT---")
    topic = state["topic"]
    
    summary_context = ""
    for i, summary_data in enumerate(state["individual_summaries"]):
        summary_context += f"Source [{i+1}] ({summary_data['url']}):\n{summary_data['summary']}\n\n---\n\n"

    prompt = f"""
    You are a world-class research analyst. Your task is to produce a high-quality, in-depth research report on the topic: "{topic}".
    The report must be based *exclusively* on the provided source summaries.

    INSTRUCTIONS:
    1.  **Structure the Report:** Organize the report into logical sections with clear, descriptive headings (e.g., Introduction, Key Findings, Market Impact, Conclusion).
    2.  **Be Comprehensive:** Synthesize information from all relevant summaries to provide a deep and detailed analysis.
    3.  **Provide Inline Citations:** For every piece of information, you MUST cite the source using the format [number].
    4.  **Do Not Hallucinate:** Do not include any information not present in the provided summaries.
    5.  **Create a References Section:** At the end of the report, create a "References" section listing all source URLs.

    Here are the source summaries:
    
    {summary_context}

    Begin the research report now:
    """
    
    response = model.generate_content(prompt)
    return {"report": response.text}

