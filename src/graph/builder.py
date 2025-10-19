from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.graph.nodes import (
    plan_queries, 
    search_web, 
    scrape_and_process, 
    ingest_and_embed,
    synthesize_initial_report
)

def build_research_graph():
    """Builds the LangGraph for the initial research and ingestion phase."""
    workflow = StateGraph(ResearchState)

    # Add the nodes for the research pipeline
    workflow.add_node("planner", plan_queries)
    workflow.add_node("searcher", search_web)
    workflow.add_node("scraper", scrape_and_process)
    workflow.add_node("ingester", ingest_and_embed)
    workflow.add_node("reporter", synthesize_initial_report)

    # Define the edges that connect the nodes in a sequence
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "scraper")
    workflow.add_edge("scraper", "ingester")
    workflow.add_edge("ingester", "reporter")
    workflow.add_edge("reporter", END)

    # Compile the workflow into a runnable application
    return workflow.compile()

