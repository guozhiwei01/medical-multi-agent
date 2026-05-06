"""
版本一：纯手写多智能体 — 入口脚本

运行方式：
    cd medical-multi-agent
    python -m v1_handwritten.main

面试话术：
    "我先用纯 Python 手写了三个 Agent 的串联，
     自己管理状态传递和错误处理，理解多智能体协作的本质。"
"""

import json
import sys
from pathlib import Path
from .pipeline import MedicalPipeline
from .llm_client import LLMClient


def load_sample_report() -> str:
    """加载示例体检报告"""
    report_path = Path(__file__).parent.parent / "sample_reports" / "sample_report_1.txt"
    if not report_path.exists():
        print(f"❌ 找不到示例报告: {report_path}")
        sys.exit(1)
    return report_path.read_text(encoding="utf-8")


def pretty_print_result(results: dict):
    """美观打印最终结果"""
    if not results["success"]:
        print(f"\n❌ 流水线执行失败: {results['error']}")
        return

    print("\n" + "🏥" * 25)
    print("   最终健康分析报告")
    print("🏥" * 25)

    # 打印建议生成Agent的输出（最终结果）
    final_output = results["steps"][-1]["output"]
    print(f"\n{final_output}")


def main():
    """主入口"""
    print("=" * 60)
    print("  🏥 医疗报告分析多智能体系统")
    print("  📋 版本一：纯手写（无框架）")
    print("=" * 60)

    # 初始化 LLM 客户端
    try:
        llm = LLMClient()
        print(f"\n✅ LLM 客户端初始化成功")
        print(f"   模型: {llm.model}")
        print(f"   API: {llm.base_url}")
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    # 加载报告
    report_text = load_sample_report()
    print(f"\n📄 已加载示例报告 ({len(report_text)} 字)")

    # 创建并运行流水线
    pipeline = MedicalPipeline(llm)
    results = pipeline.run(report_text)

    # 打印最终结果
    pretty_print_result(results)

    # 保存结果到文件
    output_path = Path(__file__).parent.parent / "output_v1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
