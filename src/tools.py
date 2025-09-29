import os
import requests
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch # CHANGED: Correct class name
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the web search tool.
# This requires a TAVILY_API_KEY in your .env file.
try:
    # CHANGED: Use the new class name
    tavily_search = TavilySearch(max_results=5)
except Exception as e:
    print(f"Failed to initialize Tavily Search Tool: {e}")
    # Set to None so the application can handle the error gracefully
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
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements to clean the text
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        return soup.get_text(" ", strip=True)
    except requests.RequestException as e:
        return f"Error scraping {url}: {e}"

