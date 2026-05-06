"""
版本三：LangGraph — 图编排

用 StateGraph 定义节点和边，编译为可执行的图。
这是 LangGraph 的核心：用图结构声明式地描述工作流。

面试话术：
    "LangGraph 用图结构让工作流更清晰可控——
     节点定义做什么，边定义执行顺序，条件边实现分支逻辑。
     比手写 if/else 更清晰，比 AutoGen 的对话模式更可控。"
"""

from langgraph.graph import StateGraph, END

from .state import MedicalState
from .nodes import (
    parse_report,
    assess_risk,
    generate_suggestions,
    generate_high_risk_suggestions,
    route_by_risk,
)


def build_graph() -> StateGraph:
    """
    构建医疗分析图。

    图结构：
        parse_report → assess_risk → [条件分支]
                                         ├─ 高风险 → generate_high_risk_suggestions → END
                                         └─ 其他   → generate_suggestions → END

    Returns:
        编译后的可执行图
    """
    # 创建图
    graph = StateGraph(MedicalState)

    # 添加节点
    graph.add_node("parse_report", parse_report)
    graph.add_node("assess_risk", assess_risk)
    graph.add_node("generate_suggestions", generate_suggestions)
    graph.add_node("generate_high_risk_suggestions", generate_high_risk_suggestions)

    # 设置入口
    graph.set_entry_point("parse_report")

    # 添加边：解析 → 评估
    graph.add_edge("parse_report", "assess_risk")

    # 添加条件边：评估 → 根据风险等级分支
    graph.add_conditional_edges(
        "assess_risk",
        route_by_risk,
        {
            "high_risk": "generate_high_risk_suggestions",
            "normal": "generate_suggestions",
        },
    )

    # 两个建议节点都通向终点
    graph.add_edge("generate_suggestions", END)
    graph.add_edge("generate_high_risk_suggestions", END)

    # 编译
    compiled = graph.compile()
    return compiled


def visualize_graph():
    """
    生成图的可视化表示（Mermaid 格式）。
    可以直接粘贴到 README 里展示。
    """
    graph = build_graph()
    try:
        print(graph.get_graph().draw_mermaid())
    except Exception:
        # 简单的文本表示
        print("""
        ┌─────────────────┐
        │  parse_report    │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  assess_risk     │
        └────────┬────────┘
                 │
           ┌─────┴─────┐
           │  路由判断   │
           └─────┬─────┘
          高风险  │  其他
        ┌────────▼──┐  ┌──▼────────────┐
        │ 高风险建议  │  │  标准建议     │
        └────────┬──┘  └──┬────────────┘
                 │        │
                 └────┬───┘
                      │
                 ┌────▼───┐
                 │  END    │
                 └────────┘
        """)
