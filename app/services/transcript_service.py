from pathlib import Path
from datetime import datetime


def save_transcript(session_id: str, messages: list, summary: dict):

    transcripts_dir = Path("test_transcripts")

    transcripts_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = transcripts_dir / f"{timestamp}_{session_id}.md"

    lines = []

    lines.append("# Closira AI Conversation Transcript\n")

    lines.append(f"Session ID: {session_id}\n")

    lines.append("---\n")

    # CONVERSATION

    lines.append("## Conversation\n")

    for msg in messages:

        role = msg["role"].capitalize()

        content = msg["content"]

        lines.append(f"**{role}:** {content}\n")

    # SUMMARY

    lines.append("\n---\n")

    lines.append("## Session Summary\n")

    for key, value in summary.items():

        lines.append(f"### {key}\n")

        lines.append(f"{value}\n")

    file_path.write_text("\n".join(lines), encoding="utf-8")

    return file_path
