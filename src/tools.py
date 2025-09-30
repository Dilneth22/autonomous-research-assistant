import os
import requests
from bs4 import BeautifulSoup
# CHANGED: Import the tool that gives structured results
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the web search tool
try:
    # CHANGED: Use the tool that returns a list of dictionaries
    tavily_search = TavilySearchResults(max_results=5)
except Exception as e:
    print(f"Failed to initialize Tavily Search Tool: {e}")
    tavily_search = None

def scrape_webpage(url: str) -> str:
    """
    Scrapes the text content from a single webpage.
    Returns the cleaned text or an error message.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # ADD THIS LINE to create the soup object
        soup = BeautifulSoup(response.text, "html.parser")
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        return soup.get_text(" ", strip=True)
    except requests.RequestException as e:
        return f"Error scraping {url}: {e}"

