"""Seed data script for OfferPilot Campus demo.

Creates sample profiles, job posts, and pre-computed results
for presentation and testing.

Usage:
    python seed_data.py
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import async_session_factory, create_all_tables
from app.models.profile import UserProfile
from app.models.job import JobPost
from app.models.match import MatchResult
from app.models.application import Application
from app.utils.id_utils import gen_id


# --- Sample Data ---

SAMPLE_PROFILES = [
    {
        "id": "demo-profile-xiaolin",
        "name": "小林",
        "school": "北京师范大学",
        "major": "市场营销",
        "grade": "大四",
        "graduation_year": 2026,
        "target_positions": ["产品经理", "市场运营", "数据分析"],
        "target_cities": ["北京", "上海", "杭州"],
        "salary_min": 8000,
        "salary_max": 15000,
        "target_industries": ["互联网", "科技", "教育"],
        "avoid_items": ["996", "外包岗位"],
        "resume_raw_text": """小林
北京师范大学 市场营销专业 大四
手机：138-0000-0000 | 邮箱：xiaolin@example.com

教育背景：
北京师范大学 市场营销（本科）2022.09 - 2026.06
GPA: 3.5/4.0，获校级二等奖学金

实习经历：
1. 字节跳动 市场运营实习生 2025.06 - 2025.09
   - 负责抖音创作者社区运营，策划3场线上活动，触达用户50万+
   - 使用Excel和SQL分析创作者数据，输出周报12份
   - 协助搭建创作者激励体系，参与产品需求评审5次

2. 新东方 用户增长实习生 2025.01 - 2025.04
   - 运营微信公众号，产出推文20篇，平均阅读量3000+
   - 使用问卷星收集用户反馈，整理分析报告4份
   - 参与用户分层策略制定，触达精准用户2万+

项目经历：
1. 校园电商数据分析项目 2024.09 - 2024.12
   - 使用Python(Pandas)清洗3万条交易数据，发现3个核心用户画像
   - 用Tableau制作可视化仪表盘，输出分析报告
   - 项目获课程优秀项目奖

2. 中国市场营销大赛 2024.03 - 2024.06
   - 带领4人团队为某教育品牌制定营销方案
   - 负责竞品分析和用户调研（发放问卷500份，回收率82%）
   - 方案获省级三等奖

技能：
- 数据分析：Excel(熟练)、SQL(基础)、Python/Pandas(基础)、Tableau(入门)
- 营销工具：问卷星、公众号后台、飞瓜数据
- 办公软件：PPT(擅长)、Word、石墨文档
- 语言能力：英语CET-6(560分)

荣誉：
- 校级二等奖学金（2次）
- 中国市场营销大赛省级三等奖
- 优秀学生干部""",
        "resume_structured": {
            "education": [
                {"school": "北京师范大学", "major": "市场营销", "degree": "本科", "start_date": "2022-09", "end_date": "2026-06", "gpa": "3.5/4.0"}
            ],
            "skills": ["Excel", "SQL", "Python", "Pandas", "Tableau", "PPT", "问卷星", "公众号运营"],
            "experiences": [
                {"type": "实习", "title": "市场运营实习生", "organization": "字节跳动", "start_date": "2025-06", "end_date": "2025-09", "description": "负责抖音创作者社区运营", "achievements": ["策划3场线上活动", "触达用户50万+", "输出周报12份"], "technologies": ["Excel", "SQL"]},
                {"type": "实习", "title": "用户增长实习生", "organization": "新东方", "start_date": "2025-01", "end_date": "2025-04", "description": "运营微信公众号", "achievements": ["产出推文20篇", "平均阅读量3000+", "触达精准用户2万+"], "technologies": ["问卷星"]},
                {"type": "项目", "title": "校园电商数据分析项目", "organization": "课程项目", "start_date": "2024-09", "end_date": "2024-12", "description": "数据分析项目", "achievements": ["清洗3万条交易数据", "发现3个核心用户画像", "获课程优秀项目奖"], "technologies": ["Python", "Pandas", "Tableau"]},
            ],
            "honors": ["校级二等奖学金(2次)", "中国市场营销大赛省级三等奖", "优秀学生干部"],
            "self_intro": "市场营销专业大四学生，具备数据分析和用户运营能力，曾在字节跳动和新东方实习。"
        },
        "skill_ratings": {"Excel": 4, "SQL": 2, "Python": 2, "Tableau": 2, "PPT": 4, "公众号运营": 3},
    },
    {
        "id": "demo-profile-xiaozhang",
        "name": "小张",
        "school": "华中科技大学",
        "major": "计算机科学与技术",
        "grade": "研二",
        "graduation_year": 2027,
        "target_positions": ["后端开发", "数据工程师"],
        "target_cities": ["深圳", "广州", "上海"],
        "salary_min": 15000,
        "salary_max": 25000,
        "target_industries": ["互联网", "金融科技"],
        "avoid_items": [],
        "resume_raw_text": "小张，华中科技大学计算机研二，熟悉Python/Java/Go，有大厂实习经历...",
        "resume_structured": {
            "education": [{"school": "华中科技大学", "major": "计算机科学与技术", "degree": "硕士", "start_date": "2025-09", "end_date": "2027-06", "gpa": "3.8/4.0"}],
            "skills": ["Python", "Java", "Go", "MySQL", "Redis", "Docker", "Kubernetes"],
            "experiences": [],
            "honors": [],
            "self_intro": "计算机研究生，有大厂实习经历。"
        },
        "skill_ratings": {},
    },
    {
        "id": "demo-profile-xiaowang",
        "name": "小王",
        "school": "浙江大学",
        "major": "英语语言文学",
        "grade": "研一",
        "graduation_year": 2027,
        "target_positions": ["产品经理", "海外运营"],
        "target_cities": ["杭州", "上海"],
        "salary_min": 10000,
        "salary_max": 18000,
        "target_industries": ["跨境电商", "教育"],
        "avoid_items": [],
        "resume_raw_text": "小王，浙大英语研一，雅思8分，有海外交换经历，想转行产品经理...",
        "resume_structured": {
            "education": [{"school": "浙江大学", "major": "英语语言文学", "degree": "硕士", "start_date": "2025-09", "end_date": "2027-06", "gpa": "3.6/4.0"}],
            "skills": ["英语", "翻译", "用户调研", "Figma"],
            "experiences": [],
            "honors": [],
            "self_intro": "英语专业研究生，跨行目标产品经理。"
        },
        "skill_ratings": {},
    },
]

SAMPLE_JOBS = [
    {
        "id": "demo-job-1",
        "user_id": "demo-profile-xiaolin",
        "company_name": "字节跳动",
        "position_title": "产品经理实习生",
        "jd_raw_text": "字节跳动产品经理实习生\n工作地点：北京\n薪资：200-350元/天\n\n岗位职责：\n1. 负责产品需求分析和功能设计\n2. 跟进产品开发进度，协调研发、设计团队\n3. 分析用户数据，优化产品体验\n4. 竞品调研和市场分析\n\n任职要求：\n1. 本科及以上学历，计算机、市场营销等相关专业优先\n2. 熟悉互联网产品设计流程，有产品实习经验优先\n3. 具备数据分析能力，熟练使用Excel和SQL\n4. 良好的沟通协调能力和逻辑思维\n5. 每周至少4天，实习6个月以上",
        "responsibilities": ["产品需求分析和功能设计", "跟进开发进度", "用户数据分析", "竞品调研"],
        "hard_requirements": ["本科及以上学历", "计算机/市场营销专业优先", "Excel和SQL", "产品实习经验优先"],
        "soft_requirements": ["沟通协调能力", "逻辑思维", "每周至少4天"],
        "salary_min": 200,
        "salary_max": 350,
        "city": "北京",
        "industry": "互联网",
        "keywords": ["产品经理", "需求分析", "数据分析", "SQL", "竞品调研"],
        "quality_score": 85,
        "quality_details": {"completeness": 90, "salary_transparency": 80, "professionalism": 85},
        "risk_tags": [],
        "status": "待评估",
    },
    {
        "id": "demo-job-2",
        "user_id": "demo-profile-xiaolin",
        "company_name": "阿里云",
        "position_title": "数据分析师",
        "jd_raw_text": "阿里云数据分析师\n工作地点：杭州\n薪资：15-25K\n\n岗位职责：\n1. 负责业务数据分析和报告\n2. 搭建数据指标体系\n3. 支持产品决策和业务优化\n\n任职要求：\n1. 本科及以上学历，统计学、数学、计算机等相关专业\n2. 熟练使用SQL、Python进行数据分析\n3. 熟悉数据可视化工具（Tableau/PowerBI）\n4. 较强的逻辑分析能力和业务理解能力",
        "responsibilities": ["业务数据分析", "搭建数据指标体系", "支持产品决策"],
        "hard_requirements": ["本科及以上学历", "统计学/数学/计算机专业", "SQL", "Python", "Tableau/PowerBI"],
        "soft_requirements": ["逻辑分析能力", "业务理解能力"],
        "salary_min": 15000,
        "salary_max": 25000,
        "city": "杭州",
        "industry": "云计算",
        "keywords": ["数据分析", "SQL", "Python", "Tableau", "指标体系"],
        "quality_score": 90,
        "quality_details": {"completeness": 95, "salary_transparency": 90, "professionalism": 85},
        "risk_tags": [],
        "status": "待评估",
    },
    {
        "id": "demo-job-3",
        "user_id": "demo-profile-xiaolin",
        "company_name": "某教育公司",
        "position_title": "用户运营",
        "jd_raw_text": "用户运营\n薪资面议\n\n要求：有运营经验即可，学历不限",
        "responsibilities": ["用户运营"],
        "hard_requirements": ["有运营经验"],
        "soft_requirements": [],
        "salary_min": None,
        "salary_max": None,
        "city": "",
        "industry": "",
        "keywords": ["运营"],
        "quality_score": 25,
        "quality_details": {"completeness": 20, "salary_transparency": 10, "professionalism": 30},
        "risk_tags": ["信息模糊", "薪资不透明"],
        "status": "待评估",
    },
]

SAMPLE_MATCH_RESULT = {
    "id": "demo-match-1",
    "user_id": "demo-profile-xiaolin",
    "job_id": "demo-job-1",
    "total_score": 72,
    "opportunity_level": "值得尝试",
    "dimension_scores": {
        "education": {"score": 75, "detail": "本科对口，北师大985背景加分"},
        "skills": {"score": 65, "detail": "Excel熟练，SQL基础，满足基本要求"},
        "experience": {"score": 80, "detail": "有字节跳动实习经历，高度相关"},
        "projects": {"score": 70, "detail": "数据分析项目和营销大赛与岗位相关"},
        "soft_requirements": {"score": 68, "detail": "沟通能力通过团队项目和实习体现"}
    },
    "matched_evidence": [
        {"jd_requirement": "数据分析能力", "resume_evidence": "使用Python/Pandas清洗3万条交易数据", "evidence_source": "简历-项目经历-校园电商项目", "strength": "强"},
        {"jd_requirement": "产品实习经验优先", "resume_evidence": "字节跳动市场运营实习生，参与产品需求评审5次", "evidence_source": "简历-实习经历-字节跳动", "strength": "强"},
        {"jd_requirement": "Excel和SQL", "resume_evidence": "Excel(熟练)，SQL(基础)，使用SQL分析创作者数据", "evidence_source": "简历-技能+实习经历", "strength": "中"},
        {"jd_requirement": "沟通协调能力", "resume_evidence": "带领4人团队完成营销大赛项目", "evidence_source": "简历-项目经历-营销大赛", "strength": "中"},
    ],
    "gaps": [
        {"jd_requirement": "产品设计流程熟悉", "severity": "中", "suggestion": "补充1-2个产品设计相关的个人项目或课程作业，展示PRD撰写能力"},
        {"jd_requirement": "SQL精通", "severity": "中", "suggestion": "SQL目前为基础水平，建议在简历中标注'学习中'并补充1个SQL实战项目"},
        {"jd_requirement": "实习6个月以上", "severity": "低", "suggestion": "确认可实习时长，如无法满足可在面试中说明灵活性"},
    ],
    "risks": [
        {"risk": "非计算机/技术专业，可能在简历筛选中被部分HR过滤", "level": "中", "mitigation": "在简历摘要中强调'数据分析能力'和'技术项目经历'"},
        {"risk": "SQL能力标注为'基础'，可能不符合JD的'熟练使用'要求", "level": "中", "mitigation": "快速提升SQL技能，在简历中如实标注学习进度"},
    ],
    "improvement_actions": [
        "在简历摘要中加入'具备数据分析和产品思维'的表述",
        "将字节跳动实习中的'参与产品需求评审5次'前置，突出产品相关经验",
        "补充SQL学习进度说明，如'正在通过LeetCode刷题提升SQL能力'",
        "在求职意向中明确写'产品经理/数据分析方向'",
    ],
}

SAMPLE_APPLICATION = {
    "id": "demo-app-1",
    "user_id": "demo-profile-xiaolin",
    "job_id": "demo-job-1",
    "job_title": "产品经理实习生",
    "company_name": "字节跳动",
    "status": "已评估",
    "match_score": 72,
    "next_action": "优化简历后投递",
    "next_action_deadline": datetime(2026, 5, 15),
    "notes": "字节跳动PM实习，匹配度较高，需要补充SQL项目",
    "tags": ["重点关注", "互联网"],
    "timeline": [
        {"time": "2026-05-09 14:00", "action": "导入岗位", "detail": "从文本粘贴导入"},
        {"time": "2026-05-09 14:05", "action": "运行匹配", "detail": "匹配分72，值得尝试"},
    ],
}


async def seed():
    """Insert seed data into the database."""
    await create_all_tables()

    async with async_session_factory() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        count = await session.execute(select(func.count()).select_from(UserProfile))
        if count.scalar() > 0:
            print("数据库已有数据，跳过种子数据注入。")
            print("如需重新注入，请先删除 backend/data/offerpilot.db")
            return

        # Insert profiles
        for p in SAMPLE_PROFILES:
            profile = UserProfile(**p)
            session.add(profile)
        print(f"✅ 注入 {len(SAMPLE_PROFILES)} 个用户画像")

        # Insert jobs
        for j in SAMPLE_JOBS:
            job = JobPost(**j)
            session.add(job)
        print(f"✅ 注入 {len(SAMPLE_JOBS)} 个岗位")

        # Insert match result
        match = MatchResult(**SAMPLE_MATCH_RESULT)
        session.add(match)
        print(f"✅ 注入 1 个匹配结果")

        # Insert application
        app = Application(**SAMPLE_APPLICATION)
        session.add(app)
        print(f"✅ 注入 1 个申请记录")

        await session.commit()
        print("\n🎉 种子数据注入完成！")
        print(f"   演示用户ID: demo-profile-xiaolin (小林)")
        print(f"   演示岗位ID: demo-job-1 (字节跳动PM实习)")


if __name__ == "__main__":
    asyncio.run(seed())
