from typing import override, Any
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph_sdk.errors import APIConnectionError
from openai import RateLimitError, InternalServerError


class AdvancedChatModel:

    wrapped_chat: ChatOpenAI
    fallback_models: list[str]

    def __init__(
        self,
        model: str,
        fallback_models: list[str],
        **kwargs: Any
    ):
        self.wrapped_chat = ChatOpenAI(
            model=model,
            **kwargs
        )
        self.fallback_models = fallback_models or []
        self.fallback_models.insert(0, model)


    def invoke(
        self,
        input: dict,
        config: RunnableConfig | None = None,
        **kwargs: Any
    ) -> AIMessage:
        response = None
        for model in self.fallback_models:
            try:
                response = self.wrapped_chat.invoke(input=input, config=config, model=model, **kwargs)
                response.content = self._remove_reasoning_block(response.content)
                return response
            except Exception as e:
                if model == self.fallback_models[-1]:
                    raise e
        return response


    async def ainvoke(
            self,
            input: dict,
            config: RunnableConfig | None = None,
            **kwargs: Any
    ) -> AIMessage:
        response = None
        for model in self.fallback_models:
            try:
                response = await self.wrapped_chat.ainvoke(input=input, config=config, model=model, **kwargs)
                response.content = self._remove_reasoning_block(response.content)
                return response
            except Exception as e:
                if model == self.fallback_models[-1]:
                    raise e
        return response


    @staticmethod
    def _remove_reasoning_block(response: str) -> str:
        try:
            end_reasoning_tag = "</thought>"
            end = response.index(end_reasoning_tag) + len(end_reasoning_tag)
            return response[end:].strip()
        except ValueError:
            return response