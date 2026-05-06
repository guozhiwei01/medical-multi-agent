"""
Agent 基类

所有 Agent 共享的基础结构：
- 持有 LLM 客户端
- 定义 system_prompt
- 统一的 run() 接口
"""

from abc import ABC, abstractmethod
from ..llm_client import LLMClient


class BaseAgent(ABC):
    """Agent 抽象基类"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.name: str = "BaseAgent"
        self.system_prompt: str = ""

    @abstractmethod
    def run(self, input_data: str) -> str:
        """
        执行 Agent 任务。

        Args:
            input_data: 上一个 Agent 的输出或用户输入

        Returns:
            Agent 处理结果（字符串形式）
        """
        ...

    def _call_llm(self, user_message: str) -> str:
        """调用 LLM 的便捷方法"""
        print(f"\n{'='*50}")
        print(f"🤖 [{self.name}] 正在处理...")
        print(f"{'='*50}")

        response = self.llm.chat(self.system_prompt, user_message)

        print(f"✅ [{self.name}] 处理完成")
        return response
