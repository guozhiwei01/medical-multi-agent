"""
LLM 客户端封装

使用 OpenAI 兼容接口，支持通义千问/豆包等国产大模型。
统一封装，三个版本共用。
"""

import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class LLMClient:
    """OpenAI 兼容的 LLM 客户端"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        # 优先使用传入参数，其次使用环境变量
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model or os.getenv("LLM_MODEL", "qwen-plus")

        if not self.api_key:
            raise ValueError(
                "未找到 API Key！请在 .env 文件中设置 DASHSCOPE_API_KEY，"
                "或通过参数传入 api_key。"
            )

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, system_prompt: str, user_message: str) -> str:
        """
        发送一轮对话，返回模型回复文本。

        Args:
            system_prompt: 系统提示词，定义 Agent 角色
            user_message: 用户输入内容

        Returns:
            模型回复的文本内容
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,  # 医疗场景偏低温度，更严谨
        )
        return response.choices[0].message.content
