import json
from datetime import datetime
from pathlib import Path


def log_escalation(
    session_id: str,
    reason: str,
    user_message: str,
    confidence_score: float = 0.0,
    sop_supported: bool = False,
):
    """
    Log escalation events to logs/escalations.log

    Args:
        session_id: Unique session identifier
        reason: Reason for escalation
        user_message: Original user message
        confidence_score: LLM confidence (0.0-1.0)
        sop_supported: Whether SOP supports the answer
    """
    log_path = Path("logs/escalations.log")

    # Create logs directory if it doesn't exist
    log_path.parent.mkdir(exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "reason": reason,
        "user_message": user_message,
        "confidence_score": confidence_score,
        "sop_supported": sop_supported,
    }

    # Append to log file (JSON Lines format)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
