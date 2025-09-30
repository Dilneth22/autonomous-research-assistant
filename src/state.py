from typing import List, TypedDict, Dict

class ResearchState(TypedDict):
    """
    Represents the state of our research agent.

    Attributes:
        topic: The initial research topic.
        queries: A list of search queries to be executed.
        urls: A list of URLs found from the search.
        documents: A list of processed documents scraped from the URLs.
        individual_summaries: A list of summaries for each document.
        report: The final, synthesized research report.
    """
    topic: str
    queries: List[str]
    urls: List[str]
    documents: List[Dict[str, str]]
    individual_summaries: List[Dict[str, str]] # This line is added/updated
    report: str

