"""
Agent1: 报告解析 Agent

职责：接收原始体检报告文本，提取关键健康指标，输出结构化 JSON。
这是流水线的第一个环节——把非结构化文本转为结构化数据。
"""

from .base import BaseAgent

SYSTEM_PROMPT = """你是一个专业的医疗报告解析专家。你的任务是从体检报告中提取关键健康指标。

## 你必须提取以下类别的指标（如果报告中存在）：

1. **一般检查**：身高、体重、BMI、血压、心率
2. **血常规**：白细胞、红细胞、血红蛋白、血小板
3. **血糖**：空腹血糖、糖化血红蛋白
4. **血脂**：总胆固醇、甘油三酯、HDL-C、LDL-C
5. **肝功能**：ALT、AST、总胆红素、白蛋白
6. **肾功能**：肌酐、尿素氮、尿酸
7. **甲状腺**：TSH、FT4

## 输出格式（严格 JSON）：

```json
{
  "patient_info": {
    "name": "姓名",
    "gender": "性别",
    "age": 年龄数字,
    "exam_date": "体检日期"
  },
  "indicators": [
    {
      "category": "分类名",
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

## 注意事项：
- value 必须是数字类型，不是字符串
- 血压拆成收缩压和舒张压两个指标
- is_abnormal 根据参考范围判断
- 只输出 JSON，不要其他解释文字
"""


class ReportParserAgent(BaseAgent):
    """报告解析 Agent：从原始报告中提取结构化指标"""

    def __init__(self, llm_client):
        super().__init__(llm_client)
        self.name = "报告解析Agent"
        self.system_prompt = SYSTEM_PROMPT

    def run(self, input_data: str) -> str:
        """
        解析体检报告文本，提取关键指标。

        Args:
            input_data: 原始体检报告文本

        Returns:
            JSON 格式的结构化指标数据
        """
        prompt = f"请解析以下体检报告，提取所有关键健康指标：\n\n{input_data}"
        return self._call_llm(prompt)
