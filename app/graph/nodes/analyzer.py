from app.graph.state import ConversationState
from app.core.config import DEBUG


async def analyzer_node(state: ConversationState):

    if DEBUG:
        print("\n[Analyzer Node Executed]")

    state["customer_intent"] = "general_query"

    return state
