from app.graph.state import ConversationState

from app.services.qualification_service import QUALIFICATION_QUESTIONS

from app.prompts.qualification_prompt import QUALIFICATION_INTRO


async def qualification_node(state: ConversationState):

    print("\n[Qualification Node Executed]")

    # SKIP IF ESCALATED

    if state["escalation_required"]:
        return state

    stage = state["qualification_stage"]

    user_message = state["current_user_message"]

    # STORE PREVIOUS ANSWER

    if stage == 1:

        state["lead_data"]["business_type"] = user_message

    elif stage == 2:

        state["lead_data"]["team_size"] = user_message

    elif stage == 3:

        state["lead_data"]["current_tools"] = user_message

        state["qualification_complete"] = True

        return state

    # ASK NEXT QUESTION

    next_question = QUALIFICATION_QUESTIONS.get(stage)

    if next_question:

        if stage == 0:

            state["final_response"] += f"\n\n{QUALIFICATION_INTRO}"

        state["final_response"] += f"\n\n{next_question}"

    state["qualification_stage"] += 1

    return state
