"""Job Description structured extraction prompt template."""

JD_EXTRACT_SYSTEM = (
    "你是招聘JD解析专家。从岗位描述中提取结构化信息，严格按JSON Schema输出。"
    "不要编造任何信息，无法判断的字段使用null或空数组。"
)

JD_EXTRACT_USER_TEMPLATE = """以下是岗位描述(JD)，请提取为结构化JSON格式：

---
{jd_text}
---

请输出以下JSON结构：
{{
  "company_name": "公司名称",
  "position_title": "岗位名称",
  "responsibilities": ["职责1", "职责2"],
  "hard_requirements": ["硬性要求1（学历、专业、技能等）"],
  "soft_requirements": ["软性要求1（经验、证书、性格等）"],
  "salary_min": null,
  "salary_max": null,
  "city": "工作城市",
  "industry": "行业",
  "keywords": ["关键词1", "关键词2"],
  "quality_score": 80,
  "quality_details": {{
    "completeness": 80,
    "salary_transparency": 70,
    "professionalism": 85
  }},
  "risk_tags": ["风险标签1"]
}}

字段说明：
- salary_min/salary_max: 薪资范围（元/月），无法判断则为null
- quality_score: 岗位质量评分(1-100)，基于信息完整度、薪资透明度、JD规范度
- quality_details: 评分明细，三项各1-100分
- risk_tags: 风险标签，如"薪资异常"、"信息模糊"、"疑似外包"、"竞业限制"等
- keywords: 5-10个关键词标签

返回纯JSON，不要包含其他文字。"""


def build_jd_extract_messages(jd_text: str) -> list[dict[str, str]]:
    """Build the message list for JD extraction."""
    return [
        {"role": "system", "content": JD_EXTRACT_SYSTEM},
        {"role": "user", "content": JD_EXTRACT_USER_TEMPLATE.format(jd_text=jd_text)},
    ]
