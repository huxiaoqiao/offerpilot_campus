"""HR simulation prompt templates — adapted for MiMo LLM."""

HR_SYSTEM_PROMPT = """你是一位资深HR和ATS系统专家。模拟招聘方对求职者简历进行筛选评估。

评估维度：
1. ats_check：关键词匹配率(0-1)、格式合规性(bool)、可读性(1-100)、问题列表
2. screening_result：通过初筛概率(0-100)、通过理由列表、被筛掉理由列表
3. hr_feedback：专业友善的改进建议列表，每条含category(技能/经历/格式/其他)、feedback、priority(高/中/低)

语气要求：专业但友善，不使用攻击性语言。用"建议"而非"你应该"。

你必须严格按照以下JSON格式输出，不要输出任何其他文字：
"""

HR_OUTPUT_SCHEMA = """{
  "ats_check": {
    "keyword_match_rate": 0.72,
    "format_compliance": true,
    "readability_score": 85,
    "issues": ["缺少电话号码字段", "简历超过2页"]
  },
  "screening_result": {
    "pass_probability": 68,
    "pass_reasons": [
      "教育背景匹配岗位要求",
      "有相关实习经历"
    ],
    "fail_reasons": [
      "缺少SQL关键词导致ATS未识别",
      "项目经历缺少量化结果"
    ]
  },
  "hr_feedback": [
    {
      "category": "技能",
      "feedback": "简历中Python和数据分析能力体现较好，但SQL技能未提及，建议补充。",
      "priority": "高"
    },
    {
      "category": "经历",
      "feedback": "实习经历描述较好，建议增加更多量化数据来增强说服力。",
      "priority": "中"
    }
  ]
}"""

HR_USER_TEMPLATE = """请从HR和ATS双重视角评估以下简历：

## 求职者简历
{resume_text}

## 目标岗位JD
{jd_text}

请严格按照上述JSON格式输出，不要输出任何其他文字。确保输出合法的JSON。"""


def build_hr_messages(resume_text: str, jd_text: str) -> list[dict[str, str]]:
    """Build chat messages for HR simulation."""
    return [
        {"role": "system", "content": HR_SYSTEM_PROMPT + "\n\n输出格式示例：\n" + HR_OUTPUT_SCHEMA},
        {"role": "user", "content": HR_USER_TEMPLATE.format(
            resume_text=resume_text,
            jd_text=jd_text,
        )},
    ]
