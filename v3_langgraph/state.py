"""
版本三：LangGraph — 共享状态定义

LangGraph 的核心概念：TypedDict 定义图的共享状态。
所有节点读写同一个 State，通过字段传递数据。

面试话术：
    "LangGraph 用 TypedDict 定义共享状态，所有节点在同一个状态空间上操作，
     这比手动传递参数更清晰，也更容易调试。"
"""

from typing import TypedDict, Literal


class MedicalState(TypedDict):
    """
    医疗分析流水线的共享状态

    每个节点读取需要的字段，写入自己的输出字段。
    LangGraph 自动管理状态的合并和传递。
    """

    # 输入
    report_text: str  # 原始体检报告文本

    # Agent1 输出
    parsed_indicators: str  # 结构化指标 JSON 字符串

    # Agent2 输出
    risk_assessment: str  # 风险评估 JSON 字符串
    overall_risk_level: Literal["高风险", "中风险", "低风险", ""]  # 用于条件分支

    # Agent3 输出
    health_suggestions: str  # 健康建议 JSON 字符串

    # 元数据
    current_step: str  # 当前执行步骤
    error: str  # 错误信息
