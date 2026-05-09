"""Resume rewrite prompt templates — adapted for MiMo LLM."""

import json
from app.schemas.resume import ResumeSections

REWRITE_SYSTEM_PROMPT = """你是专业的简历优化师。根据目标岗位JD为求职者定制简历内容。

硬约束（违反任何一条即为失败）：
1. 不编造：绝不添加用户简历中不存在的经历、技能或成就
2. 可溯源：每处改写必须标注原始素材来源
3. STAR完整：项目经历必须用STAR法重写（Situation-Task-Action-Result）

改写策略：
- summary：提取JD核心关键词+用户核心优势，生成2-3句话
- skills：JD要求的技能置顶，注明熟练程度，不夸大
- experiences：用STAR法重写，Action部分融入JD关键词，Result补充量化数据
- job_intention：明确写JD中的岗位名称

你必须严格按照以下JSON格式输出，不要输出任何其他文字：
"""

REWRITE_OUTPUT_SCHEMA = """{
  "summary": {
    "content": "具备数据分析和产品思维的市场营销专业学生...",
    "source": "基于简历原文摘要+JD关键词"
  },
  "skills": {
    "content": ["Excel(熟练)", "SQL(学习中)", "Python/Pandas(基础)", "产品需求分析"],
    "changes": [
      {"skill": "产品需求分析", "action": "新增", "reason": "JD核心要求"},
      {"skill": "SQL", "action": "置顶", "reason": "JD要求熟练使用"}
    ]
  },
  "experiences": [
    {
      "original": "字节跳动市场运营实习生，负责抖音创作者社区运营...",
      "rewritten": "【Situation】字节跳动抖音创作者社区面临用户活跃度提升需求。【Task】作为市场运营实习生，负责策划线上活动并分析用户数据。【Action】策划3场线上活动，使用Excel和SQL分析创作者数据，输出周报12份。【Result】触达用户50万+，协助搭建创作者激励体系，参与产品需求评审5次。",
      "changes": ["用STAR法重写，融入产品需求评审经历", "增加量化数据：50万+触达"]
    }
  ],
  "job_intention": {
    "content": "产品经理实习生 - 字节跳动",
    "source": "基于JD岗位名称"
  }
}"""

REWRITE_USER_TEMPLATE = """请为以下求职者针对目标岗位定制简历内容：

## 原始简历
{resume_text}

## 结构化简历数据
{structured_resume_json}

## 目标岗位JD
{jd_text}

请严格按照上述JSON格式输出，不要输出任何其他文字。确保输出合法的JSON。"""


def build_rewrite_messages(
    resume_text: str,
    structured_resume_json: str,
    jd_text: str,
) -> list[dict[str, str]]:
    """Build chat messages for resume rewriting."""
    return [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT + "\n\n输出格式示例：\n" + REWRITE_OUTPUT_SCHEMA},
        {"role": "user", "content": REWRITE_USER_TEMPLATE.format(
            resume_text=resume_text,
            structured_resume_json=structured_resume_json,
            jd_text=jd_text,
        )},
    ]
