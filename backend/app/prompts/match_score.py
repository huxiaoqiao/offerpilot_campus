"""Match scoring prompt templates."""

import json
from app.schemas.match import MatchResponse

MATCH_SYSTEM_PROMPT = """你是专业的求职匹配分析师。根据求职者简历和岗位JD进行多维度匹配评分。

评分维度（5个）：
1. education（教育匹配）：学校层次、专业对口度
2. skills（技能匹配）：核心技能覆盖比例
3. experience（经验匹配）：实习/工作经历相关度
4. projects（项目匹配）：项目与岗位职责的关联度
5. soft_requirements（软性要求匹配）：沟通能力、领导力等

硬约束：
- 每个总分必须附带至少3条证据（matched_evidence）和3条缺口（gaps）
- 每条证据必须包含jd_requirement、resume_evidence、evidence_source（溯源到简历/JD位置）、strength（强/中/弱）
- 每条缺口必须包含jd_requirement、severity（高/中/低）、suggestion（具体可执行建议）
- 每条风险必须包含risk、level（高/中/低）、mitigation
- improvement_actions 是字符串数组，每个建议具体可执行
- opportunity_level映射：≥80=强力推荐，60-79=值得尝试，40-59=需要提升，<40=暂不建议
- dimension_scores 是一个对象，key是维度名，value包含score(1-100)和detail(说明文字)

你必须严格按照以下JSON格式输出，不要输出任何其他文字：
"""

MATCH_OUTPUT_SCHEMA = """{
  "total_score": 72,
  "opportunity_level": "值得尝试",
  "dimension_scores": {
    "education": {"score": 85, "detail": "本科对口，985背景加分"},
    "skills": {"score": 65, "detail": "核心技能覆盖5/7"},
    "experience": {"score": 75, "detail": "有相关实习，但时长较短"},
    "projects": {"score": 80, "detail": "项目与岗位职责高度相关"},
    "soft_requirements": {"score": 65, "detail": "沟通能力未充分体现"}
  },
  "matched_evidence": [
    {"jd_requirement": "要求1", "resume_evidence": "简历中的证据", "evidence_source": "简历-实习经历-第1项", "strength": "强"}
  ],
  "gaps": [
    {"jd_requirement": "缺口1", "severity": "高", "suggestion": "具体改进建议"}
  ],
  "risks": [
    {"risk": "风险描述", "level": "中", "mitigation": "应对措施"}
  ],
  "improvement_actions": ["具体建议1", "具体建议2"]
}"""

MATCH_USER_TEMPLATE = """请对以下求职者简历和目标岗位进行匹配评分：

## 求职者简历
{resume_text}

## 目标岗位JD
{jd_text}

请严格按照上述JSON格式输出，不要输出任何其他文字。确保输出合法的JSON。"""


def build_match_messages(resume_text: str, jd_text: str) -> list[dict[str, str]]:
    """Build chat messages for match scoring."""
    return [
        {"role": "system", "content": MATCH_SYSTEM_PROMPT + "\n\n输出格式示例：\n" + MATCH_OUTPUT_SCHEMA},
        {"role": "user", "content": MATCH_USER_TEMPLATE.format(
            resume_text=resume_text,
            jd_text=jd_text,
        )},
    ]
