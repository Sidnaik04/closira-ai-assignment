import asyncio

from langchain_core.messages import HumanMessage

from app.core.config import settings
from app.llm.factory import LLMFactory


async def main():

    llm = LLMFactory.get_llm(settings.DEFAULT_PROVIDER)

    async for chunk in llm.astream(
        [HumanMessage(content="Explain AI in one short paragraph.")]
    ):
        print(chunk.content, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
