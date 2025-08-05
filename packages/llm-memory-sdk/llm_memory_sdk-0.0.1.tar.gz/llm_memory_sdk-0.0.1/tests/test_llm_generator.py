import asyncio

from llm_memory_sdk.core.entities import Message
from tests.llm_generator_impl import LlmGeneratorImpl


def test_llm_generator_impl():
    async def _test_impl():
        generator = LlmGeneratorImpl()
        messages = [
            Message(role="user", content="hello")
        ]
        response = await generator.generate(messages)
        assert isinstance(response, str)
        assert len(response) > 0

    asyncio.run(_test_impl())
