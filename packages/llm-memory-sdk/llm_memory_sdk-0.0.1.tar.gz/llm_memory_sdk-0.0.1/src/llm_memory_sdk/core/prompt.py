import json

from llm_memory_sdk.core.entities import (
    LongTermMemoryRetrieveCheckRequest,
    LongTermMemoryRetrieveCheckResponse,
    LongTermMemoryUpdateCachedValueRequest,
    LongTermMemoryUpdateCachedValueResponse,
    ShortTermMemory,
    ShortTermMemoryUpdateRequest,
)

SHORT_TERM_MEMORY_UPDATE_SYSTEM = f"""
!!below is your input schema!!
{json.dumps(ShortTermMemoryUpdateRequest.model_json_schema())}
!!above is your input schema!!

!!below is your output schema!!
{json.dumps(ShortTermMemory.model_json_schema())}
!!above is your output schema!!

You should update the short term memory based on the incoming messages and output the updated short term memory

You should only output the updated short term memory as json, do not output anything else.
Your output should start with "{" and end with "}"
"""

LONG_TERM_MEMORY_RETRIEVE_CHECK_SYSTEM = f"""
!!below is your input schema!!
{json.dumps(LongTermMemoryRetrieveCheckRequest.model_json_schema())}
!!above is your input schema!!

!!below is your output schema!!
{json.dumps(LongTermMemoryRetrieveCheckResponse.model_json_schema())}
!!above is your output schema!!

You should check whether the cached retrieved long term memory is sufficient for the working context.

You should only output the response body as json, do not output anything else.
Your output should start with "{" and end with "}"
"""

LONG_TERM_MEMORY_UPDATE_CACHED_VALUE_SYSTEM = f"""
!!below is your input schema!!
{json.dumps(LongTermMemoryUpdateCachedValueRequest.model_json_schema())}
!!above is your input schema!!

!!below is your output schema!!
{json.dumps(LongTermMemoryUpdateCachedValueResponse.model_json_schema())}
!!above is your output schema!!

You should update the cached value of the short term memory based on the context need from relevant memory items.

You should only output the response body as json, do not output anything else.
Your output should start with "{" and end with "}"\n"""