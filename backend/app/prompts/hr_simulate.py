"""HR simulation prompt templates."""

HR_SYSTEM_PROMPT = """你是一位资深HR和ATS系统专家。模拟招聘方对求职者简历进行筛选评估。

评估维度：
1. ATS检查：关键词匹配率、格式合规性、文件可读性
2. 筛选结果：通过初筛概率、通过理由、被筛掉理由
3. HR反馈：专业友善的改进建议

语气要求：专业但友善，不使用攻击性语言。用"建议"而非"你应该"。"""

HR_USER_TEMPLATE = """请从HR和ATS双重视角评估以下简历：

## 求职者简历
{resume_text}

## 目标岗位JD
{jd_text}

请严格按照JSON Schema输出评估结果。"""


def build_hr_messages(resume_text: str, jd_text: str) -> list[dict[str, str]]:
    """Build chat messages for HR simulation."""
    return [
        {"role": "system", "content": HR_SYSTEM_PROMPT},
        {"role": "user", "content": HR_USER_TEMPLATE.format(
            resume_text=resume_text,
            jd_text=jd_text,
        )},
    ]
