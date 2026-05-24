import asyncio
import uuid

from app.graph.builder import build_graph
from app.graph.nodes.qualification import qualification_node
from app.db.repository import create_session, save_message, save_summary
from app.graph.nodes.summary import summary_node
from app.services.transcript_service import save_transcript


async def main():

    graph = build_graph()

    state = {
        "session_id": str(uuid.uuid4()),
        "messages": [],
        "current_user_message": "",
        "customer_intent": "",
        "faq_interaction_count": 0,
        "escalation_required": False,
        "escalation_reason": "",
        "conversation_mode": "faq",
        "pending_question": "",
        "confidence_score": 0.0,
        "unanswered_questions": 0,
        "lead_data": {},
        "qualification_stage": 0,
        "qualification_complete": False,
        "sop_supported": True,
        "final_response": "",
        "summary": {},
    }

    await create_session(state["session_id"])

    print("\n=== Closira AI Support ===\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "/summary"]:
            print("\nSession ended.\n")

            summary_result = await summary_node(state)

            await save_summary(state["session_id"], summary_result["summary"])

            print("\n=== SESSION SUMMARY ===\n")

            print(summary_result["summary"])

            print("\nSession ended.\n")

            transcript_path = save_transcript(
                session_id=state["session_id"],
                messages=state["messages"],
                summary=summary_result["summary"],
            )

            print(f"\nTranscript saved to: " f"{transcript_path}")

            break

        # RESET TURN-LEVEL VALUES

        state["current_user_message"] = user_input
        state["final_response"] = ""

        # SAVE MESSAGE

        state["messages"].append({"role": "user", "content": user_input})

        await save_message(state["session_id"], "user", user_input)

        # RUN GRAPH

        if state["conversation_mode"] == "qualification":
            result = await qualification_node(state)
        else:
            result = await graph.ainvoke(state)

        ai_response = result["final_response"]

        print(f"\nAI: {ai_response}\n")

        # SAVE AI RESPONSE

        state["messages"].append({"role": "assistant", "content": ai_response})

        await save_message(state["session_id"], "assistant", ai_response)

        # UPDATE STATE

        state = result


if __name__ == "__main__":
    asyncio.run(main())
