"""
版本二：AutoGen 多智能体 — Agent 定义

使用 AutoGen 0.7+ 新版 API：
- AssistantAgent 替代旧版 ConversableAgent
- OpenAIChatCompletionClient 作为模型客户端
- 异步运行（async/await）

面试话术：
    "AutoGen 简化了 Agent 对话协作，我不需要手动传递中间状态，
     框架通过消息机制自动完成了 Agent 间的通信。"
"""

import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get_model_client() -> OpenAIChatCompletionClient:
    """创建 AutoGen 0.7+ 的 OpenAI 兼容模型客户端"""
    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL", "qwen-plus"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
        },
    )


# ============================================
# Agent1: 报告解析 Agent
# ============================================

PARSER_SYSTEM_MESSAGE = """你是一个专业的医疗报告解析专家。你的唯一任务是从体检报告中提取关键健康指标。

收到体检报告后，你必须提取所有关键指标，输出严格 JSON 格式：

```json
{
  "patient_info": {
    "name": "姓名", "gender": "性别", "age": 年龄, "exam_date": "日期"
  },
  "indicators": [
    {
      "category": "分类",
      "name": "指标中文名",
      "abbr": "英文缩写",
      "value": 数值,
      "unit": "单位",
      "reference_range": "参考范围",
      "is_abnormal": true/false
    }
  ]
}
```

注意：血压拆分为收缩压和舒张压。value 必须是数字。只输出 JSON。
完成后回复 TERMINATE。"""

# ============================================
# Agent2: 风险评估 Agent
# ============================================

ASSESSOR_SYSTEM_MESSAGE = """你是一个资深的健康风险评估专家。你会收到结构化的体检指标数据。

你的任务是评估每项指标的风险等级，并给出总体风险判定。

风险判定规则：
- 有 ≥2 项高风险 → 总体高风险
- 有 1 项高风险或 ≥3 项中风险 → 总体中风险
- 其余 → 总体低风险

输出严格 JSON 格式：
```json
{
  "overall_risk": "高/中/低风险",
  "risk_summary": "一句话总结",
  "indicator_risks": [
    {
      "name": "指标名",
      "value": 数值,
      "unit": "单位",
      "reference_range": "正常范围",
      "risk_level": "高/中/低风险",
      "description": "说明"
    }
  ],
  "high_risk_count": 数字,
  "medium_risk_count": 数字,
  "low_risk_count": 数字
}
```

只输出 JSON，不要其他文字。完成后回复 TERMINATE。"""

# ============================================
# Agent3: 建议生成 Agent
# ============================================

SUGGESTER_SYSTEM_MESSAGE = """你是一位经验丰富的家庭医生健康顾问。你会收到风险评估结果。

你的任务是生成专业、实用、有温度的健康建议。

输出严格 JSON 格式：
```json
{
  "greeting": "个性化问候",
  "urgent_actions": [
    {"title": "标题", "reason": "原因", "action": "具体措施", "department": "科室"}
  ],
  "diet_suggestions": [
    {"title": "标题", "details": "方案", "foods_to_eat": [], "foods_to_avoid": []}
  ],
  "exercise_suggestions": [
    {"title": "标题", "details": "方案", "frequency": "频率", "duration": "时长"}
  ],
  "lifestyle_suggestions": ["建议1", "建议2"],
  "follow_up": {
    "next_checkup": "时间",
    "key_indicators": ["指标"],
    "monitoring": "自我监测建议"
  },
  "encouragement": "鼓励话语"
}
```

只输出 JSON，不要其他文字。完成后回复 TERMINATE。"""


def create_agents() -> tuple[AssistantAgent, AssistantAgent, AssistantAgent]:
    """
    创建三个专业 Agent。

    AutoGen 0.7+ 关键概念：
    - AssistantAgent: 内置 LLM 的智能 Agent
    - OpenAIChatCompletionClient: 统一的模型客户端
    - 异步执行：所有操作都是 async
    """
    model_client = get_model_client()

    # Agent1: 报告解析
    parser_agent = AssistantAgent(
        name="报告解析专家",
        model_client=model_client,
        system_message=PARSER_SYSTEM_MESSAGE,
    )

    # Agent2: 风险评估
    assessor_agent = AssistantAgent(
        name="风险评估专家",
        model_client=model_client,
        system_message=ASSESSOR_SYSTEM_MESSAGE,
    )

    # Agent3: 建议生成
    suggester_agent = AssistantAgent(
        name="健康顾问",
        model_client=model_client,
        system_message=SUGGESTER_SYSTEM_MESSAGE,
    )

    return parser_agent, assessor_agent, suggester_agent
