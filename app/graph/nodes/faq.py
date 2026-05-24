import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state import ConversationState

from app.core.config import settings, DEBUG
from app.llm.factory import LLMFactory

from app.prompts.faq_prompt import FAQ_SYSTEM_PROMPT
from app.prompts.qualification_prompt import QUALIFICATION_INTRO
from app.services.sop_loader import load_sop
from app.services.escalation_logger import log_escalation
from app.services.qualification_service import QUALIFICATION_FLOW
from app.services.router_service import (
    should_start_qualification,
    should_offer_consultation,
)


async def faq_node(state: ConversationState):

    print("\n[FAQ Node Executed]")

    llm = LLMFactory.get_llm(settings.DEFAULT_PROVIDER)

    sop_text = load_sop()

    user_message = state["current_user_message"]

    # START QUALIFICATION FLOW

    if state["conversation_mode"] == "faq" and should_start_qualification(user_message):

        state["conversation_mode"] = "qualification"

        state["qualification_stage"] = 1

        state["pending_question"] = QUALIFICATION_FLOW[0]["question"]

        state["final_response"] = (
            f"{QUALIFICATION_INTRO.strip()}\n\n" f"{QUALIFICATION_FLOW[0]['question']}"
        )

        return state

    messages = [
        SystemMessage(content=FAQ_SYSTEM_PROMPT),
        HumanMessage(content=f"""
SOP:

{sop_text}

Customer Question:
{user_message}
"""),
    ]

    response = await llm.ainvoke(messages)

    if DEBUG:
        print("LLM RAW: ", response.content)

    try:

        cleaned_response = (
            response.content.replace("```json", "").replace("```", "").strip()
        )

        parsed_response = json.loads(cleaned_response)

        if DEBUG:
            print("\nPARSED RESPONSE:\n")

        # Validate consistency: if requires_escalation is true, sop_supported should be false
        if parsed_response.get("requires_escalation", False) and parsed_response.get(
            "sop_supported", False
        ):
            parsed_response["sop_supported"] = False
            if DEBUG:
                print(
                    "[CONSISTENCY FIX] Corrected sop_supported to false (was true but requires_escalation is true)"
                )

        if parsed_response["confidence"] < 0.6 or not parsed_response["sop_supported"]:
            state["escalation_required"] = True
            # Log escalation
            reason = (
                "low_confidence"
                if parsed_response["confidence"] < 0.6
                else "sop_unsupported"
            )
            log_escalation(
                session_id=state["session_id"],
                reason=reason,
                user_message=user_message,
                confidence_score=parsed_response.get("confidence", 0.0),
                sop_supported=parsed_response.get("sop_supported", False),
            )
            if DEBUG:
                print(parsed_response)

    except Exception as e:

        if DEBUG:
            print("\nJSON PARSE ERROR:\n")
            print(e)

        parsed_response = {
            "response": (
                "I’m unable to answer confidently. "
                "I’ll escalate this to a human agent."
            ),
            "confidence": 0.0,
            "sop_supported": False,
            "requires_escalation": True,
        }
        # Log escalation due to parsing error
        log_escalation(
            session_id=state["session_id"],
            reason="json_parse_error",
            user_message=user_message,
            confidence_score=0.0,
            sop_supported=False,
        )
    state["final_response"] = parsed_response["response"]

    state["confidence_score"] = parsed_response["confidence"]

    state["sop_supported"] = parsed_response["sop_supported"]
    if parsed_response["requires_escalation"]:
        state["escalation_required"] = True
        # Log if not already logged above
        if not (
            parsed_response["confidence"] < 0.6 or not parsed_response["sop_supported"]
        ):
            log_escalation(
                session_id=state["session_id"],
                reason="requires_escalation_flag",
                user_message=user_message,
                confidence_score=parsed_response.get("confidence", 0.0),
                sop_supported=parsed_response.get("sop_supported", False),
            )

    # AFTER SUCCESSFUL FAQ RESPONSE: track interactions and optionally offer consultation
    try:
        # increment FAQ interaction counter
        state["faq_interaction_count"] = state.get("faq_interaction_count", 0) + 1

        if not state.get("qualification_complete", False) and should_offer_consultation(
            user_message,
            state["faq_interaction_count"],
        ):
            state.setdefault("final_response", "")
            state["final_response"] += (
                "\n\nWould you like to book " "a free consultation?"
            )
            state["booking_suggested"] = True
    except Exception:
        pass

    return state
