from app.graph.state import ConversationState

from app.services.qualification_service import QUALIFICATION_FLOW

async def qualification_node(state: ConversationState):

    print("\n[Qualification Node Executed]")

    stage = state["qualification_stage"]

    user_message = state["current_user_message"]

    # STORE PREVIOUS ANSWER

    if stage > 0:

        previous = QUALIFICATION_FLOW[stage - 1]

        state["lead_data"][previous["field"]] = user_message

    # CHECK COMPLETION

    if stage >= len(QUALIFICATION_FLOW):

        state["qualification_complete"] = True

        state["conversation_mode"] = "faq"

        state["final_response"] = (
            "Thank you for the information. " "Our team will contact you shortly."
        )

        return state

    # ASK NEXT QUESTION

    current = QUALIFICATION_FLOW[stage]

    question = current["question"]

    state["pending_question"] = question

    state["final_response"] = question

    state["qualification_stage"] += 1

    return state
