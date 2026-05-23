import asyncio

from langchain_core.messages import HumanMessage

from app.core.config import settings
from app.llm.factory import LLMFactory


async def main():

    llm = LLMFactory.get_llm(settings.DEFAULT_PROVIDER)

    response = await llm.ainvoke([
        HumanMessage(content="Say hello in one sentence and greet.")
    ])

    print("\nAI RESPONSE:\n")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())