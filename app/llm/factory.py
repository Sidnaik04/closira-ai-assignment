from app.llm.providers import (
    get_openai_llm,
    get_gemini_llm,
    get_claude_llm
)


class LLMFactory:

    @staticmethod
    def get_llm(provider: str):

        provider = provider.lower()

        if provider == "openai":
            return get_openai_llm()

        if provider == "claude":
            return get_claude_llm()

        return get_gemini_llm()