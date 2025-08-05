from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel

from .convention import LlmGenerator
from .entities import Message

T = TypeVar('T', bound=BaseModel)

class StructuredLlmGenerator:

    def __init__(self, llm_generator: LlmGenerator):
        self.llm_generator = llm_generator

    async def generate(self, messages: Sequence[Message], output_type: type[T]) -> T:
        raw_output = await self.llm_generator.generate(messages)
        first_brace = raw_output.find('{')
        last_brace = raw_output.rfind('}')
        if first_brace == -1 or last_brace == -1 or first_brace > last_brace:
            raise ValueError("No valid JSON-like content found in the output")
        json_content = raw_output[first_brace:last_brace + 1]
        return output_type.model_validate_json(json_content)