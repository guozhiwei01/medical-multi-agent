"""
版本三：LangGraph 多智能体 — 入口脚本

运行方式：
    cd medical-multi-agent
    python -m v3_langgraph.main

核心优势（面试话术）：
    "LangGraph 用图结构定义工作流，我可以：
     1. 声明式地定义节点和边，代码即文档
     2. 条件分支——高风险走加强路径，低风险走标准路径
     3. 未来可以轻松加入并行节点、循环、人机交互等
     4. 自动生成流程图，方便和团队沟通"
"""

import json
import sys
import time
from pathlib import Path

from .graph import build_graph, visualize_graph


def load_sample_report() -> str:
    """加载示例体检报告"""
    report_path = Path(__file__).parent.parent / "sample_reports" / "sample_report_1.txt"
    if not report_path.exists():
        print(f"❌ 找不到示例报告: {report_path}")
        sys.exit(1)
    return report_path.read_text(encoding="utf-8")


def main():
    """LangGraph 版本的主流程"""
    print("=" * 60)
    print("  🏥 医疗报告分析多智能体系统")
    print("  📋 版本三：LangGraph 图编排")
    print("=" * 60)

    # 打印图结构
    print("\n📐 图结构：")
    visualize_graph()

    # 加载报告
    report_text = load_sample_report()
    print(f"\n📄 已加载示例报告 ({len(report_text)} 字)")

    # 构建图
    graph = build_graph()
    print("✅ 图编译完成")

    # 初始状态
    initial_state = {
        "report_text": report_text,
        "parsed_indicators": "",
        "risk_assessment": "",
        "overall_risk_level": "",
        "health_suggestions": "",
        "current_step": "开始",
        "error": "",
    }

    # 执行图
    start_time = time.time()
    print("\n🚀 开始执行图...")

    final_state = graph.invoke(initial_state)

    total_time = time.time() - start_time

    # ========================================
    # 打印结果
    # ========================================
    print("\n" + "=" * 60)
    print("📊 执行摘要 (LangGraph 版)")
    print("=" * 60)
    print(f"  ✅ 报告解析节点 → 完成")
    print(f"  ✅ 风险评估节点 → 完成")
    risk_path = "高风险加强路径 🚨" if final_state["overall_risk_level"] == "高风险" else "标准路径 ✅"
    print(f"  🔀 条件路由 → {risk_path}")
    print(f"  ✅ 建议生成节点 → 完成")
    print(f"  ⏱️  总耗时: {total_time:.1f}s")
    print("=" * 60)

    # 最终结果
    print("\n" + "🏥" * 25)
    print("   最终健康分析报告 (LangGraph 版)")
    print("🏥" * 25)
    print(f"\n总体风险等级: {final_state['overall_risk_level']}")
    print(f"\n{final_state['health_suggestions']}")

    # 保存结果
    results = {
        "version": "v3_langgraph",
        "success": True,
        "total_time": f"{total_time:.1f}s",
        "risk_level": final_state["overall_risk_level"],
        "route_taken": risk_path,
        "steps": [
            {"node": "parse_report", "output": final_state["parsed_indicators"]},
            {"node": "assess_risk", "output": final_state["risk_assessment"]},
            {"node": "generate_suggestions", "output": final_state["health_suggestions"]},
        ],
    }

    output_path = Path(__file__).parent.parent / "output_v3.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
