from collections.abc import Sequence
from typing import Optional

from llm_memory_sdk.core import LlmGenerator, LongTermMemory, MemorySession
from llm_memory_sdk.core.entities import (
    MemoryItem,
    MemoryRetrieveResult,
    Message,
    ShortTermMemory,
    ShortTermMemoryUpdateRequest,
)
from llm_memory_sdk.core.prompt import SHORT_TERM_MEMORY_UPDATE_SYSTEM
from llm_memory_sdk.core.structured import StructuredLlmGenerator


class InMemoryLongTermMemory(LongTermMemory):
    _llm_generator: LlmGenerator
    _document_set: Sequence[MemoryItem]
    _cached_result: Optional[str]
    _cached_short_term_memory: Optional[ShortTermMemory]

    def __init__(
            self,
            llm_generator: LlmGenerator,
            document_set: Sequence[MemoryItem]
    ):
        self._llm_generator = llm_generator
        self._document_set = document_set
        self._cached_result = None
        self._cached_short_term_memory = None

    async def retrieve(self, short_term_memory: ShortTermMemory) -> str:
        # 如果没有缓存结果，直接从文档集中检索
        if self._cached_result is None:
            # 这里实现从文档集中检索的逻辑
            # 简单实现：将所有文档内容连接起来
            result = "\n".join([doc.content for doc in self._document_set])
            self._cached_result = result
            self._cached_short_term_memory = short_term_memory
            return result

        # 检查短期记忆是否有变化
        if self._cached_short_term_memory == short_term_memory:
            # 短期记忆没有变化，直接返回缓存结果
            return self._cached_result

        # 短期记忆有变化，需要判断是否需要更新缓存
        # 这里简化处理，直接更新缓存并返回新结果
        result = "\n".join([doc.content for doc in self._document_set])
        self._cached_result = result
        self._cached_short_term_memory = short_term_memory
        return result

    async def update(self, short_term_memory: ShortTermMemory) -> None:
        # TODO: currently as read only implementation
        pass


class MemorySessionImpl(MemorySession):
    _llm_generator: LlmGenerator
    _short_term_memory: ShortTermMemory
    _long_term_memory: LongTermMemory

    def __init__(
            self,
            llm_generator: LlmGenerator,
            short_term_memory: ShortTermMemory,
            long_term_memory: LongTermMemory
    ):
        self._llm_generator = llm_generator
        self._short_term_memory = short_term_memory
        self._long_term_memory = long_term_memory

    async def update(self, messages: Sequence[Message]) -> None:
        update_request = ShortTermMemoryUpdateRequest(
            messages=messages,
            current_short_term_memory=self._short_term_memory
        )
        structured_generator = StructuredLlmGenerator(self._llm_generator)
        self._short_term_memory = await structured_generator.generate(
            messages=[
                Message(role="system", content=SHORT_TERM_MEMORY_UPDATE_SYSTEM),
                Message(role="user", content=update_request.model_dump_json())
            ],
            output_type=ShortTermMemory
        )

    async def retrieve(self) -> MemoryRetrieveResult:
        long_term_memory_content = await self._long_term_memory.retrieve(self._short_term_memory)
        return MemoryRetrieveResult(
            short_term_memory=self._short_term_memory,
            long_term_memory=long_term_memory_content
        )
