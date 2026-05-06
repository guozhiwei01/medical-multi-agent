"""
版本三：LangGraph — 图节点定义

每个节点是一个函数：接收 State，返回 State 的部分更新。
LangGraph 会自动合并返回值到共享状态中。

面试话术：
    "LangGraph 的节点是纯函数，输入输出都是 State，
     这让每个节点可以独立测试，也方便做条件分支。"
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

from .state import MedicalState

load_dotenv(find_dotenv())


def _get_llm() -> ChatOpenAI:
    """创建 LangChain 的 ChatOpenAI 实例（兼容通义千问/豆包）"""
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "qwen-plus"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        temperature=0.3,
    )


# ============================================
# Node 1: 报告解析
# ============================================

PARSER_PROMPT = """你是一个专业的医疗报告解析专家。从体检报告中提取关键健康指标。

输出严格 JSON 格式：
{
  "patient_info": {"name": "姓名", "gender": "性别", "age": 年龄, "exam_date": "日期"},
  "indicators": [
    {"category": "分类", "name": "中文名", "abbr": "缩写", "value": 数值, "unit": "单位", "reference_range": "范围", "is_abnormal": true/false}
  ]
}

血压拆分为收缩压和舒张压。value 必须是数字。只输出 JSON。"""


def parse_report(state: MedicalState) -> dict:
    """
    节点1：解析体检报告，提取结构化指标。

    输入：state["report_text"]
    输出：state["parsed_indicators"], state["current_step"]
    """
    print(f"\n{'='*50}")
    print("🤖 [Node 1] 报告解析节点执行中...")
    print(f"{'='*50}")

    llm = _get_llm()

    response = llm.invoke([
        SystemMessage(content=PARSER_PROMPT),
        HumanMessage(content=f"请解析以下体检报告：\n\n{state['report_text']}"),
    ])

    print("✅ 报告解析完成")

    return {
        "parsed_indicators": response.content,
        "current_step": "报告解析完成",
    }


# ============================================
# Node 2: 风险评估
# ============================================

ASSESSOR_PROMPT = """你是健康风险评估专家。根据体检指标评估风险。

风险判定规则：
- ≥2 项高风险 → 总体高风险
- 1 项高风险或 ≥3 项中风险 → 总体中风险
- 其余 → 总体低风险

输出严格 JSON：
{
  "overall_risk": "高风险/中风险/低风险",
  "risk_summary": "一句话总结",
  "indicator_risks": [
    {"name": "指标名", "value": 数值, "unit": "单位", "reference_range": "范围", "risk_level": "高/中/低风险", "description": "说明"}
  ],
  "high_risk_count": 数字,
  "medium_risk_count": 数字,
  "low_risk_count": 数字
}

只输出 JSON。"""


def assess_risk(state: MedicalState) -> dict:
    """
    节点2：风险评估。

    输入：state["parsed_indicators"]
    输出：state["risk_assessment"], state["overall_risk_level"]
    """
    print(f"\n{'='*50}")
    print("🤖 [Node 2] 风险评估节点执行中...")
    print(f"{'='*50}")

    llm = _get_llm()

    response = llm.invoke([
        SystemMessage(content=ASSESSOR_PROMPT),
        HumanMessage(content=f"请评估以下指标的风险：\n\n{state['parsed_indicators']}"),
    ])

    # 尝试从返回结果中提取 overall_risk，用于条件分支
    risk_level = ""
    try:
        clean = response.content.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            lines = [l for l in lines[1:] if l.strip() != "```"]
            clean = "\n".join(lines)
        risk_data = json.loads(clean)
        risk_level = risk_data.get("overall_risk", "")
    except (json.JSONDecodeError, KeyError):
        risk_level = "中风险"  # 解析失败时默认中风险

    print(f"✅ 风险评估完成 → 总体风险: {risk_level}")

    return {
        "risk_assessment": response.content,
        "overall_risk_level": risk_level,
        "current_step": "风险评估完成",
    }


# ============================================
# Node 3: 建议生成（标准版）
# ============================================

SUGGESTER_PROMPT = """你是家庭医生健康顾问。根据风险评估生成健康建议。

输出严格 JSON：
{
  "greeting": "个性化问候",
  "urgent_actions": [{"title": "标题", "reason": "原因", "action": "措施", "department": "科室"}],
  "diet_suggestions": [{"title": "标题", "details": "方案", "foods_to_eat": [], "foods_to_avoid": []}],
  "exercise_suggestions": [{"title": "标题", "details": "方案", "frequency": "频率", "duration": "时长"}],
  "lifestyle_suggestions": ["建议1", "建议2"],
  "follow_up": {"next_checkup": "时间", "key_indicators": ["指标"], "monitoring": "监测建议"},
  "encouragement": "鼓励话语"
}

只输出 JSON。"""


def generate_suggestions(state: MedicalState) -> dict:
    """
    节点3：标准建议生成。

    用于低风险和中风险场景。
    """
    print(f"\n{'='*50}")
    print("🤖 [Node 3] 建议生成节点执行中...")
    print(f"{'='*50}")

    llm = _get_llm()

    response = llm.invoke([
        SystemMessage(content=SUGGESTER_PROMPT),
        HumanMessage(content=f"请生成健康建议：\n\n{state['risk_assessment']}"),
    ])

    print("✅ 标准建议生成完成")

    return {
        "health_suggestions": response.content,
        "current_step": "建议生成完成",
    }


# ============================================
# Node 3-alt: 建议生成（高风险加强版）
# ============================================

HIGH_RISK_PROMPT = """你是资深专科医生顾问。该患者被评估为【高风险】，需要更详尽和紧急的建议。

你必须：
1. 强调紧急就医的必要性
2. 给出详细的专科就诊路径（先看哪科，需要哪些检查）
3. 给出就医前的临时自我管理措施
4. 说明不及时处理的潜在后果

输出严格 JSON：
{
  "greeting": "严肃但关切的问候",
  "risk_alert": "⚠️ 高风险警告内容",
  "urgent_actions": [
    {"title": "标题", "reason": "原因", "action": "具体措施", "department": "科室", "urgency": "紧急程度", "tests_needed": ["需要的检查"]}
  ],
  "immediate_measures": ["就医前临时措施1", "措施2"],
  "diet_suggestions": [{"title": "标题", "details": "方案", "foods_to_eat": [], "foods_to_avoid": []}],
  "exercise_suggestions": [{"title": "标题", "details": "方案", "frequency": "频率", "duration": "时长"}],
  "lifestyle_suggestions": ["建议1", "建议2"],
  "follow_up": {"next_checkup": "时间", "key_indicators": ["指标"], "monitoring": "监测建议"},
  "potential_risks": "不处理的潜在后果说明",
  "encouragement": "鼓励话语"
}

只输出 JSON。"""


def generate_high_risk_suggestions(state: MedicalState) -> dict:
    """
    节点3-alt：高风险加强版建议生成。

    这是 LangGraph 条件分支的核心展示——
    高风险走这个节点，中/低风险走标准节点。
    """
    print(f"\n{'='*50}")
    print("🚨 [Node 3-HIGH] 高风险加强建议节点执行中...")
    print(f"{'='*50}")

    llm = _get_llm()

    response = llm.invoke([
        SystemMessage(content=HIGH_RISK_PROMPT),
        HumanMessage(content=f"该患者为高风险，请生成详尽的就医建议：\n\n{state['risk_assessment']}"),
    ])

    print("✅ 高风险加强建议生成完成")

    return {
        "health_suggestions": response.content,
        "current_step": "高风险加强建议生成完成",
    }


# ============================================
# 条件分支函数
# ============================================

def route_by_risk(state: MedicalState) -> str:
    """
    条件路由：根据风险等级决定走哪个建议生成节点。

    这是 LangGraph 相比手写版和 AutoGen 的核心优势——
    用声明式的图结构定义条件分支，而不是 if/else 硬编码。

    Returns:
        "high_risk" 或 "normal" — 对应图中的不同边
    """
    risk = state.get("overall_risk_level", "")
    print(f"\n🔀 路由判断: 总体风险 = {risk}")

    if risk == "高风险":
        print("   → 走高风险加强路径 🚨")
        return "high_risk"
    else:
        print("   → 走标准建议路径 ✅")
        return "normal"
