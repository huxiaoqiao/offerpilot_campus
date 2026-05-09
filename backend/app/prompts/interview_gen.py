"""Interview question generation prompt templates."""

INTERVIEW_SYSTEM_PROMPT = """你是面试辅导专家。根据求职者简历和目标岗位生成个性化面试准备材料。

要求：
1. 生成10-15道面试题，覆盖5个类别：自我介绍、行为面试、技术问题、情景模拟、反问环节
2. 每道题的参考答案框架必须融入用户的简历素材
3. STAR故事必须基于用户真实项目经历，不编造
4. 风险追问必须针对简历中的薄弱环节"""

INTERVIEW_USER_TEMPLATE = """请为以下求职者生成面试准备材料：

## 求职者简历
{resume_text}

## 目标岗位JD
{jd_text}

## 匹配分析（如有）
{match_summary}

请严格按照JSON Schema输出面试准备材料。"""


def build_interview_messages(
    resume_text: str,
    jd_text: str,
    match_summary: str,
) -> list[dict[str, str]]:
    """Build chat messages for interview question generation."""
    return [
        {"role": "system", "content": INTERVIEW_SYSTEM_PROMPT},
        {"role": "user", "content": INTERVIEW_USER_TEMPLATE.format(
            resume_text=resume_text,
            jd_text=jd_text,
            match_summary=match_summary,
        )},
    ]
