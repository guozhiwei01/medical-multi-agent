"""
Pipeline：手动串联三个 Agent

这是手写版本的核心——自己管理状态传递、错误处理和执行流程。
面试要点：手写需要自己管状态传递和错误处理，框架帮你做了这些。
"""

import json
import time
from .llm_client import LLMClient
from .agents import ReportParserAgent, RiskAssessmentAgent, SuggestionAgent


class MedicalPipeline:
    """
    医疗报告分析流水线

    手动串联三个 Agent：
    报告解析 → 风险评估 → 建议生成

    关键点（面试可以说的）：
    1. 状态传递：手动把上一个 Agent 的 output 传给下一个 Agent 的 input
    2. 错误处理：每一步都可能出错，需要自己 try/except
    3. 中间结果：需要自己决定是否保存中间状态
    4. 执行顺序：完全硬编码的线性流程
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

        # 初始化三个 Agent
        self.parser = ReportParserAgent(self.llm)
        self.assessor = RiskAssessmentAgent(self.llm)
        self.suggester = SuggestionAgent(self.llm)

    def run(self, report_text: str) -> dict:
        """
        执行完整的分析流水线。

        Args:
            report_text: 原始体检报告文本

        Returns:
            包含三步结果的完整字典
        """
        print("\n" + "🏥" * 25)
        print("   医疗报告分析多智能体系统 v1（纯手写版）")
        print("🏥" * 25)

        results = {
            "success": False,
            "steps": [],
            "error": None,
        }

        start_time = time.time()

        # ========================================
        # Step 1: 报告解析
        # ========================================
        try:
            step1_start = time.time()
            parsed_data = self.parser.run(report_text)
            step1_time = time.time() - step1_start

            results["steps"].append({
                "agent": "报告解析Agent",
                "status": "success",
                "time": f"{step1_time:.1f}s",
                "output": parsed_data,
            })

            # 验证输出是否为有效 JSON
            self._validate_json(parsed_data, "报告解析")

        except Exception as e:
            results["error"] = f"报告解析失败: {str(e)}"
            results["steps"].append({
                "agent": "报告解析Agent",
                "status": "failed",
                "error": str(e),
            })
            return results

        # ========================================
        # Step 2: 风险评估
        # ========================================
        try:
            step2_start = time.time()
            risk_data = self.assessor.run(parsed_data)
            step2_time = time.time() - step2_start

            results["steps"].append({
                "agent": "风险评估Agent",
                "status": "success",
                "time": f"{step2_time:.1f}s",
                "output": risk_data,
            })

            self._validate_json(risk_data, "风险评估")

        except Exception as e:
            results["error"] = f"风险评估失败: {str(e)}"
            results["steps"].append({
                "agent": "风险评估Agent",
                "status": "failed",
                "error": str(e),
            })
            return results

        # ========================================
        # Step 3: 建议生成
        # ========================================
        try:
            step3_start = time.time()
            suggestions = self.suggester.run(risk_data)
            step3_time = time.time() - step3_start

            results["steps"].append({
                "agent": "建议生成Agent",
                "status": "success",
                "time": f"{step3_time:.1f}s",
                "output": suggestions,
            })

            self._validate_json(suggestions, "建议生成")

        except Exception as e:
            results["error"] = f"建议生成失败: {str(e)}"
            results["steps"].append({
                "agent": "建议生成Agent",
                "status": "failed",
                "error": str(e),
            })
            return results

        # ========================================
        # 汇总结果
        # ========================================
        total_time = time.time() - start_time
        results["success"] = True
        results["total_time"] = f"{total_time:.1f}s"

        self._print_summary(results)
        return results

    def _validate_json(self, text: str, step_name: str) -> dict:
        """验证并解析 JSON，处理 markdown 代码块包裹的情况"""
        clean_text = text.strip()
        # 去除可能的 markdown 代码块标记
        if clean_text.startswith("```"):
            lines = clean_text.split("\n")
            # 去掉第一行 (```json) 和最后一行 (```)
            lines = [l for l in lines[1:] if l.strip() != "```"]
            clean_text = "\n".join(lines)

        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"⚠️  [{step_name}] 输出不是严格 JSON，但继续执行: {e}")
            return {}

    def _print_summary(self, results: dict):
        """打印执行摘要"""
        print("\n" + "=" * 60)
        print("📊 执行摘要")
        print("=" * 60)

        for step in results["steps"]:
            status_icon = "✅" if step["status"] == "success" else "❌"
            time_info = f" ({step.get('time', 'N/A')})" if "time" in step else ""
            print(f"  {status_icon} {step['agent']}{time_info}")

        print(f"\n  ⏱️  总耗时: {results.get('total_time', 'N/A')}")
        print(f"  {'🎉 全部成功!' if results['success'] else '❌ 执行失败: ' + str(results.get('error'))}")
        print("=" * 60)
