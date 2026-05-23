import asyncio
import uuid

from app.graph.builder import build_graph


async def main():

    graph = build_graph()

    state = {
        "session_id": str(uuid.uuid4()),
        "messages": [],
        "current_user_message": "",
        "customer_intent": "",
        "escalation_required": False,
        "escalation_reason": "",
        "confidence_score": 0.0,
        "unanswered_questions": 0,
        "lead_data": {},
        "qualification_stage": 0,
        "qualification_complete": False,
        "sop_supported": True,
        "final_response": "",
        "summary": {},
    }

    print("\n=== Closira AI Support ===\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("\nSession ended.\n")
            break

        # RESET TURN-LEVEL VALUES

        state["current_user_message"] = user_input
        state["final_response"] = ""

        # SAVE MESSAGE

        state["messages"].append({"role": "user", "content": user_input})

        # RUN GRAPH

        result = await graph.ainvoke(state)

        ai_response = result["final_response"]

        print(f"\nAI: {ai_response}\n")

        # SAVE AI RESPONSE

        state["messages"].append({"role": "assistant", "content": ai_response})

        # UPDATE STATE

        state = result


if __name__ == "__main__":
    asyncio.run(main())
