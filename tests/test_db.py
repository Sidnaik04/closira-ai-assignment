import asyncio
import uuid

from app.db.repository import create_session, get_session, save_message


async def main():

    session_id = str(uuid.uuid4())

    await create_session(session_id)

    await save_message(session_id, "user", "Hello")

    session = await get_session(session_id)

    print("\nSESSION:\n")
    print(session.session_id)


if __name__ == "__main__":

    asyncio.run(main())
