import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state import ConversationState

from app.core.config import settings
from app.llm.factory import LLMFactory

from app.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT
from app.core.config import DEBUG


async def summary_node(state: ConversationState):

    if DEBUG:
        print("\n[Summary Node Executed]")

    llm = LLMFactory.get_llm(settings.DEFAULT_PROVIDER)

    conversation_text = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in state["messages"]]
    )

    messages = [
        SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Conversation:

{conversation_text}

Lead Data:
{state["lead_data"]}

Escalation Reason:
{state["escalation_reason"]}
"""),
    ]

    response = await llm.ainvoke(messages)

    cleaned_response = (
        response.content.replace("```json", "").replace("```", "").strip()
    )

    try:

        parsed = json.loads(cleaned_response)

        state["summary"] = parsed

    except Exception as e:

        if DEBUG:
            print("\nSummary Parse Error:\n")
            print(e)

        state["summary"] = {
            "customer_intent": "unknown",
            "key_details_collected": {},
            "sop_gaps_identified": [],
            "escalation_reason": (state["escalation_reason"]),
            "recommended_next_action": ("Human review required"),
        }

    return state
