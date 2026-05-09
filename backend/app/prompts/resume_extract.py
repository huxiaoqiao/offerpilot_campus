"""Resume structured extraction prompt template."""

RESUME_EXTRACT_SYSTEM = (
    "你是简历解析专家。从简历原文中提取结构化信息，严格按JSON Schema输出。"
    "不要编造任何信息，如果某个字段无法从原文中提取，使用空字符串或空数组。"
)

RESUME_EXTRACT_USER_TEMPLATE = """以下是简历原文，请提取为结构化JSON格式：

---
{resume_text}
---

请输出以下JSON结构：
{{
  "name": "姓名",
  "phone": "手机号",
  "email": "邮箱",
  "education": [
    {{
      "school": "学校名称",
      "major": "专业",
      "degree": "学历（本科/硕士/博士等）",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "gpa": "GPA或成绩（可选）",
      "description": "描述（可选）"
    }}
  ],
  "experience": [
    {{
      "company": "公司/组织名称",
      "title": "职位/角色",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "description": "工作描述",
      "achievements": ["成就1", "成就2"]
    }}
  ],
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "technologies": ["技术栈1", "技术栈2"],
      "start_date": "开始时间",
      "end_date": "结束时间",
      "achievements": ["成果1"]
    }}
  ],
  "skills": ["技能1", "技能2", "技能3"],
  "certificates": ["证书1", "证书2"],
  "self_evaluation": "自我评价/自我介绍"
}}

返回纯JSON，不要包含其他文字。"""


def build_resume_extract_messages(resume_text: str) -> list[dict[str, str]]:
    """Build the message list for resume extraction."""
    return [
        {"role": "system", "content": RESUME_EXTRACT_SYSTEM},
        {"role": "user", "content": RESUME_EXTRACT_USER_TEMPLATE.format(resume_text=resume_text)},
    ]
