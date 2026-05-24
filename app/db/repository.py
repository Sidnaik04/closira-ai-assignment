from sqlalchemy import select

from app.db.database import AsyncSessionLocal

from app.db.models import SessionModel, MessageModel


async def create_session(session_id: str):

    async with AsyncSessionLocal() as db:

        session = SessionModel(session_id=session_id)

        db.add(session)

        await db.commit()


async def get_session(session_id: str):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )

        return result.scalar_one_or_none()


async def save_message(session_id: str, role: str, content: str):

    async with AsyncSessionLocal() as db:

        message = MessageModel(session_id=session_id, role=role, content=content)

        db.add(message)

        await db.commit()


async def save_summary(session_id: str, summary: dict):

    async with AsyncSessionLocal() as db:

        session = await db.get(SessionModel, session_id)

        if session:

            session.summary = summary

            await db.commit()
