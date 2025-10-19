from typing import List, TypedDict, Dict

class ResearchState(TypedDict):
    """
    Represents the state of our research agent, now with RAG capabilities.
    """
    # Core research state
    topic: str
    queries: List[str]
    urls: List[str]
    documents: List[Dict[str, str]]
    report: str

    # State for the persistent RAG system
    topic_index_path: str  # Path to the created vector store for the topic
    
    # State for the Q&A phase
    follow_up_question: str
    follow_up_answer: str

