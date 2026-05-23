from app.graph.state import ConversationState


async def analyzer_node(state: ConversationState):

    print("\n[Analyzer Node Executed]")

    state["customer_intent"] = "general_query"

    return state
