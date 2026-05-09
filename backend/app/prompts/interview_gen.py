"""Interview question generation prompt templates — adapted for MiMo LLM."""

INTERVIEW_SYSTEM_PROMPT = """你是面试辅导专家。根据求职者简历和目标岗位生成个性化面试准备材料。

要求：
1. 生成10-15道面试题，覆盖5个类别：自我介绍、行为面试、技术问题、情景模拟、反问环节
2. 每道题的参考答案框架必须融入用户的简历素材
3. STAR故事必须基于用户真实项目经历，不编造
4. 风险追问必须针对简历中的薄弱环节

你必须严格按照以下JSON格式输出，不要输出任何其他文字：
"""

INTERVIEW_OUTPUT_SCHEMA = """{
  "questions": [
    {
      "id": "q1",
      "category": "自我介绍",
      "question": "请用3分钟介绍你自己",
      "reference_answer_framework": "建议从教育背景(北师大市场营销)切入，突出字节跳动实习中的数据分析经验，引出对产品经理岗位的热情",
      "related_resume_item": "简历-教育背景+实习经历-字节跳动",
      "related_risk": null
    },
    {
      "id": "q2",
      "category": "行为面试",
      "question": "请描述一次你在团队中解决冲突的经历",
      "reference_answer_framework": "使用STAR法，建议从市场营销大赛4人团队经历中提取素材，突出协调沟通能力",
      "related_resume_item": "简历-项目经历-市场营销大赛",
      "related_risk": null
    },
    {
      "id": "q3",
      "category": "技术问题",
      "question": "你如何进行竞品分析？",
      "reference_answer_framework": "结合市场营销大赛中的竞品分析经验，展示系统化的分析框架",
      "related_resume_item": "简历-项目经历-市场营销大赛",
      "related_risk": "产品设计流程不熟悉"
    }
  ],
  "star_stories": [
    {
      "title": "校园电商数据分析项目",
      "situation": "课程要求对校园电商平台数据进行分析",
      "task": "需要清洗3万条交易数据并发现核心用户画像",
      "action": "使用Python(Pandas)清洗数据，用Tableau制作可视化仪表盘",
      "result": "发现3个核心用户画像，项目获课程优秀项目奖",
      "applicable_questions": ["数据分析能力", "项目管理", "技术能力"]
    }
  ],
  "risk_followups": [
    {
      "risk": "产品设计流程不熟悉",
      "possible_question": "你没有直接的产品经理实习经历，如何证明你能胜任？",
      "suggested_answer": "强调在字节跳动参与了5次产品需求评审，自学了产品设计方法论，并通过数据分析项目展示了产品思维"
    }
  ]
}"""

INTERVIEW_USER_TEMPLATE = """请为以下求职者生成面试准备材料：

## 求职者简历
{resume_text}

## 目标岗位JD
{jd_text}

## 匹配分析（如有）
{match_summary}

请严格按照上述JSON格式输出，不要输出任何其他文字。确保输出合法的JSON。"""


def build_interview_messages(
    resume_text: str,
    jd_text: str,
    match_summary: str,
) -> list[dict[str, str]]:
    """Build chat messages for interview question generation."""
    return [
        {"role": "system", "content": INTERVIEW_SYSTEM_PROMPT + "\n\n输出格式示例：\n" + INTERVIEW_OUTPUT_SCHEMA},
        {"role": "user", "content": INTERVIEW_USER_TEMPLATE.format(
            resume_text=resume_text,
            jd_text=jd_text,
            match_summary=match_summary,
        )},
    ]
