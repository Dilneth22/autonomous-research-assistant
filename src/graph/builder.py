from langgraph.graph import StateGraph, END
from src.state import ResearchState  # CHANGED: Absolute import
from src.graph.nodes import plan_queries, search_web, scrape_and_process, synthesize_report  # CHANGED: Absolute import

def build_graph():
    """
    Builds the LangGraph workflow for the autonomous research agent.
    This function defines the structure and flow of the agent's operations.
    """
    # Initialize a new state graph with the defined ResearchState structure
    workflow = StateGraph(ResearchState)

    # Add the nodes to the graph. Each node corresponds to an agent's function.
    workflow.add_node("planner", plan_queries)
    workflow.add_node("searcher", search_web)
    workflow.add_node("scraper", scrape_and_process)
    workflow.add_node("synthesizer", synthesize_report)

    # Define the edges that connect the nodes, setting the sequence of operations.
    workflow.set_entry_point("planner")  # The workflow starts with the planner
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "scraper")
    workflow.add_edge("scraper", "synthesizer")
    workflow.add_edge("synthesizer", END)  # The workflow ends after the synthesizer

    # Compile the graph into a runnable application
    app = workflow.compile()
    return app

