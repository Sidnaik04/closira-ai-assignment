LEAD_CONFIRMATION_KEYWORDS = [
    "yes",
    "sure",
    "okay",
    "ok",
    "interested",
    "book",
    "consultation",
]

INTEREST_KEYWORDS = ["book", "booking", "consultation", "appointment", "interested"]


def should_start_qualification(user_message: str):

    user_message = user_message.lower()

    return any(keyword in user_message for keyword in LEAD_CONFIRMATION_KEYWORDS)


def should_offer_consultation(user_message: str, faq_count: int):

    user_message = user_message.lower()

    if faq_count >= 2:
        return True

    return any(keyword in user_message for keyword in INTEREST_KEYWORDS)
