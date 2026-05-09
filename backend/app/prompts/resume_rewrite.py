"""Resume rewrite prompt templates."""

REWRITE_SYSTEM_PROMPT = """你是专业的简历优化师。根据目标岗位JD为求职者定制简历内容。

硬约束（违反任何一条即为失败）：
1. 不编造：绝不添加用户简历中不存在的经历、技能或成就
2. 可溯源：每处改写必须标注原始素材来源
3. STAR完整：项目经历必须用STAR法重写（Situation-Task-Action-Result）
4. 用户确认：改写结果由用户确认后才生效

改写策略：
- 摘要：提取JD核心关键词+用户核心优势，生成2-3句话
- 技能：JD要求的技能置顶，注明熟练程度，不夸大
- 项目：用STAR法重写，Action部分融入JD关键词，Result补充量化数据
- 求职意向：明确写JD中的岗位名称"""

REWRITE_USER_TEMPLATE = """请为以下求职者针对目标岗位定制简历内容：

## 原始简历
{resume_text}

## 结构化简历数据
{structured_resume_json}

## 目标岗位JD
{jd_text}

请严格按照JSON Schema输出改写结果。"""


def build_rewrite_messages(
    resume_text: str,
    structured_resume_json: str,
    jd_text: str,
) -> list[dict[str, str]]:
    """Build chat messages for resume rewriting."""
    return [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
        {"role": "user", "content": REWRITE_USER_TEMPLATE.format(
            resume_text=resume_text,
            structured_resume_json=structured_resume_json,
            jd_text=jd_text,
        )},
    ]
