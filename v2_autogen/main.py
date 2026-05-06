"""
版本二：AutoGen 多智能体 — 入口脚本

运行方式：
    cd medical-multi-agent
    python -m v2_autogen.main

核心区别（vs 手写版）：
    - 不需要手动传递状态，AutoGen 通过 Agent.run() 自动管理消息
    - Agent 是异步执行的
    - 框架自动处理了消息格式和对话管理
"""

import asyncio
import json
import sys
import time
from pathlib import Path

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from .agents import create_agents


def load_sample_report() -> str:
    """加载示例体检报告"""
    report_path = Path(__file__).parent.parent / "sample_reports" / "sample_report_1.txt"
    if not report_path.exists():
        print(f"❌ 找不到示例报告: {report_path}")
        sys.exit(1)
    return report_path.read_text(encoding="utf-8")


async def run_pipeline():
    """
    AutoGen 版本的主流程（异步）。

    使用 Agent.on_messages() 让每个 Agent 独立处理任务，
    然后手动传递结果给下一个 Agent。
    """
    print("=" * 60)
    print("  🏥 医疗报告分析多智能体系统")
    print("  📋 版本二：AutoGen 框架")
    print("=" * 60)

    # 加载报告
    report_text = load_sample_report()
    print(f"\n📄 已加载示例报告 ({len(report_text)} 字)")

    # 创建 Agent
    parser, assessor, suggester = create_agents()
    print("✅ Agent 创建完成")

    start_time = time.time()
    cancel_token = CancellationToken()

    # ========================================
    # Step 1: 报告解析
    # ========================================
    print(f"\n{'='*50}")
    print("🤖 [Step 1] 报告解析专家处理中...")
    print(f"{'='*50}")

    step1_response = await parser.on_messages(
        [TextMessage(content=f"请解析以下体检报告，提取所有关键健康指标：\n\n{report_text}", source="user")],
        cancel_token,
    )
    parsed_data = step1_response.chat_message.content
    print(f"✅ 报告解析完成")

    # ========================================
    # Step 2: 风险评估（传入解析结果）
    # ========================================
    print(f"\n{'='*50}")
    print("🤖 [Step 2] 风险评估专家处理中...")
    print(f"{'='*50}")

    step2_response = await assessor.on_messages(
        [TextMessage(content=f"请对以下体检指标进行风险评估：\n\n{parsed_data}", source="user")],
        cancel_token,
    )
    risk_data = step2_response.chat_message.content
    print(f"✅ 风险评估完成")

    # ========================================
    # Step 3: 建议生成（传入评估结果）
    # ========================================
    print(f"\n{'='*50}")
    print("🤖 [Step 3] 健康顾问处理中...")
    print(f"{'='*50}")

    step3_response = await suggester.on_messages(
        [TextMessage(content=f"请根据以下风险评估结果，为患者生成个性化的健康管理建议：\n\n{risk_data}", source="user")],
        cancel_token,
    )
    suggestions = step3_response.chat_message.content
    print(f"✅ 建议生成完成")

    # ========================================
    # 汇总
    # ========================================
    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("📊 执行摘要 (AutoGen 版)")
    print("=" * 60)
    print(f"  ✅ 报告解析专家 → 完成")
    print(f"  ✅ 风险评估专家 → 完成")
    print(f"  ✅ 健康顾问 → 完成")
    print(f"  ⏱️  总耗时: {total_time:.1f}s")
    print("=" * 60)

    # 打印最终结果
    print("\n" + "🏥" * 25)
    print("   最终健康分析报告 (AutoGen 版)")
    print("🏥" * 25)
    print(f"\n{suggestions}")

    # 保存结果
    results = {
        "version": "v2_autogen",
        "success": True,
        "total_time": f"{total_time:.1f}s",
        "steps": [
            {"agent": "报告解析专家", "output": parsed_data},
            {"agent": "风险评估专家", "output": risk_data},
            {"agent": "健康顾问", "output": suggestions},
        ],
    }

    output_path = Path(__file__).parent.parent / "output_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {output_path}")


def main():
    """同步入口"""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
