import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state import ConversationState

from app.core.config import settings
from app.llm.factory import LLMFactory

from app.prompts.faq_prompt import FAQ_SYSTEM_PROMPT
from app.services.sop_loader import load_sop
from app.services.escalation_logger import log_escalation


async def faq_node(state: ConversationState):

    print("\n[FAQ Node Executed]")

    llm = LLMFactory.get_llm(settings.DEFAULT_PROVIDER)

    sop_text = load_sop()

    user_message = state["current_user_message"]

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
    print("LLM RAW: ", response.content)

    try:

        cleaned_response = (
            response.content.replace("```json", "").replace("```", "").strip()
        )

        parsed_response = json.loads(cleaned_response)

        print("\nPARSED RESPONSE:\n")

        # Validate consistency: if requires_escalation is true, sop_supported should be false
        if parsed_response.get("requires_escalation", False) and parsed_response.get(
            "sop_supported", False
        ):
            parsed_response["sop_supported"] = False
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
            print(parsed_response)

    except Exception as e:

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

    # Suggest booking if SOP supported the answer and message implies booking intent
    try:
        if (
            not state.get("escalation_required", False)
            and parsed_response.get("sop_supported", False)
            and parsed_response.get("confidence", 0.0) >= 0.6
        ):
            booking_keywords = ["price", "consultation", "booking", "service"]
            lower_msg = (user_message or "").lower()
            if any(k in lower_msg for k in booking_keywords):
                state.setdefault("final_response", "")
                state[
                    "final_response"
                ] += "\n\nWould you like to book a free consultation?"
                state["booking_suggested"] = True
    except Exception:
        pass

    return state
