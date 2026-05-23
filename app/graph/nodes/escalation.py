import json
import logging

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from app.graph.state import ConversationState

from app.core.config import settings
from app.core.constants import (
    MEDICAL_KEYWORDS,
    COMPLAINT_KEYWORDS,
    NEGOTIATION_KEYWORDS,
    HUMAN_HANDOFF_KEYWORDS
)

from app.llm.factory import LLMFactory

from app.prompts.escalation_prompt import (
    ESCALATION_SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


async def escalation_node(state: ConversationState):

    print("\n[Escalation Node Executed]")

    user_message = (
        state["current_user_message"].lower()
    )

    escalation_reason = None

    # RULE-BASED DETECTION

    if any(
        keyword in user_message
        for keyword in MEDICAL_KEYWORDS
    ):
        escalation_reason = "medical_question"

    elif any(
        keyword in user_message
        for keyword in COMPLAINT_KEYWORDS
    ):
        escalation_reason = "complaint"

    elif any(
        keyword in user_message
        for keyword in NEGOTIATION_KEYWORDS
    ):
        escalation_reason = "pricing_negotiation"

    elif any(
        keyword in user_message
        for keyword in HUMAN_HANDOFF_KEYWORDS
    ):
        escalation_reason = "human_request"

    # IF RULES MATCHED

    if escalation_reason:

        state["escalation_required"] = True
        state["escalation_reason"] = escalation_reason

        logger.warning(
            f"Escalation Triggered: {escalation_reason}"
        )

        return state

    # SEMANTIC ANALYSIS

    llm = LLMFactory.get_llm(
        settings.DEFAULT_PROVIDER
    )

    messages = [
        SystemMessage(
            content=ESCALATION_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=user_message
        )
    ]

    response = await llm.ainvoke(messages)

    cleaned_response = (
        response.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        parsed = json.loads(cleaned_response)

        if parsed["escalate"]:

            state["escalation_required"] = True
            state["escalation_reason"] = (
                parsed["reason"]
            )

            logger.warning(
                f"LLM Escalation: {parsed['reason']}"
            )

    except Exception as e:

        print("\nEscalation Parse Error:\n")
        print(e)

    return state