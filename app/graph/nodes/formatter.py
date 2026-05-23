from app.graph.state import ConversationState


async def formatter_node(state: ConversationState):

    print("\n[Formatter Node Executed]")

    if state["escalation_required"]:

        if not state["final_response"]:

            state["final_response"] = (
                "I’m escalating this conversation " "to a human support agent."
            )

        else:

            state["final_response"] += (
                "\n\nI’m escalating this conversation " "to a human support agent."
            )

    return state
