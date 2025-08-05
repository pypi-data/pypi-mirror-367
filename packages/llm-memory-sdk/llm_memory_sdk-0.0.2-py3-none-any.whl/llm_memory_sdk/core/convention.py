from abc import ABC, abstractmethod
from collections.abc import Sequence

from .entities import MemoryRetrieveResult, Message, ShortTermMemory


class LongTermMemory(ABC):
    @abstractmethod
    async def retrieve(self, short_term_memory: ShortTermMemory) -> str:
        raise NotImplementedError

    @abstractmethod
    async def update(self, short_term_memory: ShortTermMemory) -> None:
        raise NotImplementedError


class MemorySession(ABC):
    @abstractmethod
    async def update(self, messages: Sequence[Message]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def retrieve(self) -> MemoryRetrieveResult:
        raise NotImplementedError

class LlmGenerator(ABC):
    @abstractmethod
    async def generate(self, messages: Sequence[Message]) -> str:
        raise NotImplementedError