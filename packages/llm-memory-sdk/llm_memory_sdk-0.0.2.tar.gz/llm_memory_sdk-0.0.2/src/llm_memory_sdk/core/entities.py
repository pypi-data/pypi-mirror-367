from collections.abc import Sequence

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """A memory item that stores information on specific fields for the current context."""
    id: str = Field(description="A unique name in ASCII for this memory item")
    abstract: str = Field(description="A short summary of this memory item's content")
    content: str = Field(description="The content of this memory item, containing information for current context")


class MemoryItemAbstract(BaseModel):
    """An abstract for a memory item, specifying it's content."""
    id: str = Field(description="A unique name in ASCII for this memory item")
    abstract: str = Field(description="A short summary of this memory item's content")


class Message(BaseModel):
    """An message or tool call in a LLM agent process."""
    role: str = Field(description="The role of the message sender, can be user, assistant, or tool")
    content: str = Field(description="The content of the message")


class ShortTermMemory(BaseModel):
    """Short-term memory that contains all the information for the current task's context."""
    open_files: MemoryItem = Field(description="Relevant information on opened files for current task. If not relevant, throw it away.")  # noqa: E501
    plan: MemoryItem = Field(description="Plan and it's process for the current task. Should be updated when a step is done or plan changed.")  # noqa: E501
    current_work_info: MemoryItem = Field(description="Information on the current step working on.")
    guidelines: MemoryItem = Field(description="User's instructions and rules you must follow. Can be extracted from user's message.")  # noqa: E501
    context_info: MemoryItem = Field(description="Background information, knowledge, experience and information on current context.")  # noqa: E501 


class MemoryRetrieveResult(BaseModel):
    short_term_memory: ShortTermMemory
    long_term_memory: str

class ShortTermMemoryUpdateRequest(BaseModel):
    messages: Sequence[Message] = Field(description="Incoming agent messages that may contain new information.")
    current_short_term_memory: ShortTermMemory = Field(description="Current short-term memory that maybe need to update.")  # noqa: E501

class LongTermMemoryRetrieveCheckRequest(BaseModel):
    short_term_memory: ShortTermMemory = Field(description="Current short-term memory that indicates working context.")
    cached_result: str = Field(description="Cached result from previous retrieve.")
    memory_abstracts: Sequence[MemoryItemAbstract] = Field(description="Abstracts of all memory items in long-term memory.")  # noqa: E501

class LongTermMemoryRetrieveCheckResponse(BaseModel):
    update: bool = Field(description="Whether the cached_result needs to be updated with information in long-term memory.")  # noqa: E501
    relevant_memory_names: Sequence[str] = Field(description="Names of memory items that are relevant to the current context.")  # noqa: E501

class LongTermMemoryUpdateCachedValueRequest(BaseModel):
    short_term_memory: ShortTermMemory = Field(description="Current short-term memory that indicates working context.")
    cached_result: str = Field(description="Cached result from previous retrieve.")
    relevant_memory_items: Sequence[MemoryItem] = Field(description="Memory items that are relevant to the current context.")  # noqa: E501

class LongTermMemoryUpdateCachedValueResponse(BaseModel):
    updated_cached_result: str = Field(description="Updated cached result.")