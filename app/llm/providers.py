from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic


def get_openai_llm():
    from app.core.config import settings

    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4.1-mini",
        temperature=0,
        streaming=True,
    )


def get_gemini_llm():
    from app.core.config import settings

    return ChatGoogleGenerativeAI(
        google_api_key=settings.GOOGLE_API_KEY,
        model=settings.MODEL_NAME,
        temperature=0,
        streaming=True,
    )


def get_claude_llm():
    from app.core.config import settings

    return ChatAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        model="claude-3-5-sonnet-latest",
        temperature=0,
        streaming=True,
    )
