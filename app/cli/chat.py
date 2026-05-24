import asyncio
import os
import uuid
import getpass
from rich.console import Console
from rich.panel import Panel

from app.graph.builder import build_graph
from app.graph.nodes.qualification import qualification_node
from app.db.repository import create_session, save_message, save_summary
from app.graph.nodes.summary import summary_node
from app.services.transcript_service import save_transcript

console = Console()


def setup_llm_provider():
    """Interactive setup for LLM provider and API key."""
    console.print("\n[bold cyan]LLM Provider Setup[/bold cyan]\n")

    providers = {
        "1": ("gemini", "GOOGLE_API_KEY"),
        "2": ("openai", "OPENAI_API_KEY"),
        "3": ("claude", "ANTHROPIC_API_KEY"),
    }

    console.print("[bold yellow]Select LLM Provider:[/bold yellow]")
    console.print("  1. Gemini (Google)")
    console.print("  2. OpenAI")
    console.print("  3. Claude (Anthropic)\n")

    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice in providers:
            provider_name, env_var = providers[choice]
            break
        console.print("[bold red]Invalid choice. Please enter 1, 2, or 3.[/bold red]\n")

    api_key = getpass.getpass(f"Enter your {provider_name.upper()} API key: ")

    if not api_key.strip():
        console.print("[bold red]API key cannot be empty.[/bold red]")
        return setup_llm_provider()

    # Set environment variable
    os.environ[env_var] = api_key

    console.print(
        f"\n[bold green]✓ Provider set to {provider_name.upper()}[/bold green]\n"
    )
    return provider_name


def display_summary(summary):
    """Format and display session summary cleanly."""
    console.print("\n=== SESSION SUMMARY ===")
    console.print(f"\n[bold]Customer Intent:[/bold]")
    console.print(f"  {summary.get('customer_intent', 'N/A')}")

    console.print(f"\n[bold]Key Details:[/bold]")
    details = summary.get("key_details_collected", {})
    if details:
        for key, value in details.items():
            console.print(f"  - {key}: {value}")
    else:
        console.print("  None")

    console.print(f"\n[bold]Escalation Reason:[/bold]")
    escalation = summary.get("escalation_reason") or "None"
    console.print(f"  {escalation}")

    console.print(f"\n[bold]Recommended Next Action:[/bold]")
    console.print(f"  {summary.get('recommended_next_action', 'N/A')}")


async def main():
    # Setup LLM provider and API key
    setup_llm_provider()

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

    console.print(Panel.fit("[bold cyan]Closira AI Support Agent[/bold cyan]"))
    console.print(
        "[bold yellow]/summary[/bold yellow] - Session summary  |  [bold yellow]/help[/bold yellow] - Commands  |  [bold yellow]/exit[/bold yellow] - Quit\n"
    )

    while True:

        console.print("\n[bold blue][you][/bold blue]")
        user_input = input("> ")

        if user_input.lower() == "/help":
            console.print("\n[bold yellow]Commands:[/bold yellow]")
            console.print("  /summary - Generate and display session summary")
            console.print("  /clear   - Clear the screen")
            console.print("  /help    - Show this help message")
            console.print("  /exit    - Exit session\n")
            continue

        if user_input.lower() == "/clear":
            os.system("clear")
            continue

        if user_input.lower() in ["exit", "quit", "/summary"]:
            summary_result = await summary_node(state)
            await save_summary(state["session_id"], summary_result["summary"])
            display_summary(summary_result["summary"])
            transcript_path = save_transcript(
                session_id=state["session_id"],
                messages=state["messages"],
                summary=summary_result["summary"],
            )
            console.print(f"\n[dim]Transcript saved: {transcript_path}[/dim]\n")
            break

        state["current_user_message"] = user_input
        state["final_response"] = ""
        state["messages"].append({"role": "user", "content": user_input})
        await save_message(state["session_id"], "user", user_input)

        if state["conversation_mode"] == "qualification":
            result = await qualification_node(state)
        else:
            result = await graph.ainvoke(state)

        ai_response = result["final_response"]
        console.print("\n[bold cyan][Closira AI][/bold cyan]")

        if result.get("escalation_required", False):
            console.print(ai_response, style="bold red")
        else:
            console.print(ai_response, style="bold green")

        state["messages"].append({"role": "assistant", "content": ai_response})
        await save_message(state["session_id"], "assistant", ai_response)
        state = result


if __name__ == "__main__":
    asyncio.run(main())
