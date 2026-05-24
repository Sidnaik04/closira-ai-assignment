from typing import TypedDict, List, Dict, Any


class ConversationState(TypedDict):

    session_id: str

    messages: List[Dict[str, str]]

    current_user_message: str

    customer_intent: str
    
    faq_interaction_count: int

    escalation_required: bool
    escalation_reason: str

    conversation_mode: str

    pending_question: str

    confidence_score: float

    unanswered_questions: int

    lead_data: Dict[str, Any]

    qualification_stage: int
    qualification_complete: bool

    sop_supported: bool

    final_response: str

    summary: Dict[str, Any]
