import asyncio

from app.db.database import engine, Base

import app.db.models


async def init_models():

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

    print("\nDatabase initialized.\n")


if __name__ == "__main__":

    asyncio.run(init_models())
