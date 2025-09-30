from langgraph.graph import StateGraph, END
from src.state import ResearchState
# Import the new node for individual summarization
from src.graph.nodes import plan_queries, search_web, scrape_and_process, summarize_documents_individually, synthesize_report

def build_graph():
    """Builds the LangGraph research agent."""
    workflow = StateGraph(ResearchState)

    # Add all the agent nodes to the graph
    workflow.add_node("planner", plan_queries)
    workflow.add_node("searcher", search_web)
    workflow.add_node("scraper", scrape_and_process)
    workflow.add_node("summarizer", summarize_documents_individually) # The new summarizer step
    workflow.add_node("synthesizer", synthesize_report)

    # Define the edges to connect the nodes in the correct order
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "scraper")
    workflow.add_edge("scraper", "summarizer") # Scraper now goes to the summarizer
    workflow.add_edge("summarizer", "synthesizer") # Summarizer goes to the final synthesizer
    workflow.add_edge("synthesizer", END)

    # Compile the graph into a runnable application
    app = workflow.compile()
    return app

