from langgraph.graph import StateGraph, END

from app.graph.state import ConversationState

from app.graph.nodes.analyzer import analyzer_node
from app.graph.nodes.faq import faq_node
from app.graph.nodes.formatter import formatter_node


def escalation_router(state: ConversationState):

    if state["escalation_required"]:
        return "formatter"

    return "faq"


def build_graph():

    workflow = StateGraph(ConversationState)

    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("faq", faq_node)
    workflow.add_node("formatter", formatter_node)

    workflow.set_entry_point("analyzer")

    # Run FAQ immediately after analysis; escalation is checked inside nodes or by flags
    workflow.add_edge("analyzer", "faq")
    workflow.add_edge("faq", "formatter")

    workflow.add_edge("formatter", END)

    return workflow.compile()
