from sqlalchemy import String, Text, Boolean, JSON

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SessionModel(Base):

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)

    conversation_mode: Mapped[str] = mapped_column(String, default="faq")

    qualification_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    escalation_required: Mapped[bool] = mapped_column(Boolean, default=False)

    escalation_reason: Mapped[str] = mapped_column(String, default="")

    lead_data: Mapped[dict] = mapped_column(JSON, default={})

    summary: Mapped[dict] = mapped_column(JSON, default={})


class MessageModel(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    session_id: Mapped[str] = mapped_column(String)

    role: Mapped[str] = mapped_column(String)

    content: Mapped[str] = mapped_column(Text)
