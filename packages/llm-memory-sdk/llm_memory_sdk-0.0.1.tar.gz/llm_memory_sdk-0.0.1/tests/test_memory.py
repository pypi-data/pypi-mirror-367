import asyncio
from collections.abc import Sequence

from llm_memory_sdk.core import LongTermMemory, MemorySession
from llm_memory_sdk.core.entities import MemoryItem, Message, ShortTermMemory
from llm_memory_sdk.core.implementation import InMemoryLongTermMemory, MemorySessionImpl
from tests.llm_generator_impl import LlmGeneratorImpl


def test_short_term_and_long_term_memory():
    """
    测试短期记忆和长期记忆的效果
    由于记忆效果无法量化，仅在控制台输出展示
    """
    async def _test_impl():
        # 创建模拟的长期记忆数据
        long_term_memory_docs: Sequence[MemoryItem] = [
            MemoryItem(
                id="project_info",
                abstract="项目信息",
                content="这是一个LLM记忆SDK项目，用于管理AI助手的短期和长期记忆"
            ),
            MemoryItem(
                id="api_keys",
                abstract="API密钥信息",
                content="项目需要配置ALIBABA_QWEN_API_KEY环境变量才能使用Qwen大模型"
            ),
            MemoryItem(
                id="memory_structure",
                abstract="记忆结构",
                content="短期记忆包括打开的文件、计划、当前工作信息、指南和上下文信息"
            )
        ]
        
        # 初始化组件
        llm_generator = LlmGeneratorImpl()
        long_term_memory: LongTermMemory = InMemoryLongTermMemory(
            llm_generator=llm_generator,
            document_set=long_term_memory_docs
        )
        
        # 创建初始短期记忆
        initial_short_term_memory = ShortTermMemory(
            open_files=MemoryItem(
                id="current_file",
                abstract="当前处理的文件",
                content="正在处理test_memory.py测试文件"
            ),
            plan=MemoryItem(
                id="test_plan",
                abstract="测试计划",
                content="编写测试用例演示短期记忆和长期记忆的效果"
            ),
            current_work_info=MemoryItem(
                id="current_task",
                abstract="当前任务",
                content="实现和运行记忆功能的测试"
            ),
            guidelines=MemoryItem(
                id="coding_guidelines",
                abstract="编码指南",
                content="按照项目规范编写测试代码，确保输出清晰展示记忆效果"
            ),
            context_info=MemoryItem(
                id="task_context",
                abstract="任务上下文",
                content="需要展示短期记忆的更新和长期记忆的检索过程"
            )
        )
        
        # 创建记忆会话
        memory_session: MemorySession = MemorySessionImpl(
            llm_generator=llm_generator,
            short_term_memory=initial_short_term_memory,
            long_term_memory=long_term_memory
        )
        
        print("=" * 60)
        print("记忆功能演示")
        print("=" * 60)
        
        # 第一次检索记忆
        print("\n1. 初始记忆状态:")
        print("-" * 30)
        memory_result = await memory_session.retrieve()
        print(f"短期记忆 - 打开文件: {memory_result.short_term_memory.open_files.content}")
        print(f"短期记忆 - 计划: {memory_result.short_term_memory.plan.content}")
        print(f"短期记忆 - 当前工作: {memory_result.short_term_memory.current_work_info.content}")
        print(f"长期记忆内容:\n{memory_result.long_term_memory}")
        
        # 模拟对话更新短期记忆
        print("\n2. 模拟对话后更新短期记忆:")
        print("-" * 30)
        messages = [
            Message(
                role="user", 
                content="请重点关注项目信息和API密钥部分，我需要配置环境变量"
            )
        ]
        await memory_session.update(messages)
        
        # 再次检索记忆
        memory_result = await memory_session.retrieve()
        print(f"短期记忆 - 打开文件: {memory_result.short_term_memory.open_files.content}")
        print(f"短期记忆 - 计划: {memory_result.short_term_memory.plan.content}")
        print(f"短期记忆 - 当前工作: {memory_result.short_term_memory.current_work_info.content}")
        print(f"短期记忆 - 指南: {memory_result.short_term_memory.guidelines.content}")
        print(f"短期记忆 - 上下文: {memory_result.short_term_memory.context_info.content}")
        print(f"长期记忆内容:\n{memory_result.long_term_memory}")
        
        # 模拟另一轮对话
        print("\n3. 另一轮对话后的记忆状态:")
        print("-" * 30)
        messages = [
            Message(
                role="user",
                content="现在我们测试一下只关注记忆结构部分的场景"
            )
        ]
        await memory_session.update(messages)
        
        # 再次检索记忆
        memory_result = await memory_session.retrieve()
        print(f"短期记忆 - 打开文件: {memory_result.short_term_memory.open_files.content}")
        print(f"短期记忆 - 计划: {memory_result.short_term_memory.plan.content}")
        print(f"短期记忆 - 当前工作: {memory_result.short_term_memory.current_work_info.content}")
        print(f"长期记忆内容:\n{memory_result.long_term_memory}")
        
        print("\n" + "=" * 60)
        print("演示完成")
        print("=" * 60)

    asyncio.run(_test_impl())


if __name__ == "__main__":
    test_short_term_and_long_term_memory()