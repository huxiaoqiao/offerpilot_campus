"""ResumeService - AI-powered resume tailoring with version management."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import llm_client
from app.models.job import JobPost
from app.models.profile import UserProfile
from app.models.resume import ResumeVersion
from app.prompts.resume_rewrite import build_rewrite_messages
from app.schemas.resume import ResumeRewriteResponse, ResumeSections
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)


class ResumeService:
    """Async service for resume rewriting and version management."""

    async def rewrite_resume(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> ResumeRewriteResponse:
        """Generate a tailored resume for a specific job and store it."""
        profile = await self._get_profile(db, user_id)
        job = await self._get_job(db, job_id)

        resume_text = profile.resume_raw_text or ""
        jd_text = job.jd_raw_text or ""
        structured_json = json.dumps(profile.resume_structured or {}, ensure_ascii=False)

        if not resume_text:
            raise HTTPException(status_code=400, detail="User has no resume text")
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job has no JD text")

        messages = build_rewrite_messages(resume_text, structured_json, jd_text)
        # Use chat() + manual parsing for MiMo LLM compatibility
        raw_text = await llm_client.chat(messages, max_tokens=4000)
        from app.llm.output_parser import parse_json_output, validate_schema
        data = parse_json_output(raw_text)
        sections = validate_schema(data, ResumeSections)

        # Determine next version number
        max_ver_result = await db.execute(
            select(func.max(ResumeVersion.version)).where(
                ResumeVersion.user_id == user_id,
                ResumeVersion.job_id == job_id,
            )
        )
        next_version = (max_ver_result.scalar() or 0) + 1

        # Generate HTML preview
        html_preview = self._generate_html(
            user_name=profile.name,
            sections=sections,
            profile=profile,
        )

        record = ResumeVersion(
            id=gen_id(),
            user_id=user_id,
            job_id=job_id,
            version=next_version,
            sections=sections.model_dump(),
            html_preview=html_preview,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        return ResumeRewriteResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            version=record.version,
            sections=sections,
            html_preview=html_preview,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def get_resume(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> ResumeRewriteResponse:
        """Get the latest resume version for a job."""
        result = await db.execute(
            select(ResumeVersion)
            .where(
                ResumeVersion.user_id == user_id,
                ResumeVersion.job_id == job_id,
            )
            .order_by(ResumeVersion.version.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="No resume version found")
        return self._to_response(record)

    async def get_resume_versions(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> list[ResumeRewriteResponse]:
        """Get all resume versions for a job, newest first."""
        result = await db.execute(
            select(ResumeVersion)
            .where(
                ResumeVersion.user_id == user_id,
                ResumeVersion.job_id == job_id,
            )
            .order_by(ResumeVersion.version.desc())
        )
        records = result.scalars().all()
        return [self._to_response(r) for r in records]

    async def get_resume_html(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> str:
        """Get the HTML preview of the latest resume version."""
        result = await db.execute(
            select(ResumeVersion)
            .where(
                ResumeVersion.user_id == user_id,
                ResumeVersion.job_id == job_id,
            )
            .order_by(ResumeVersion.version.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if not record or not record.html_preview:
            raise HTTPException(status_code=404, detail="No resume HTML found")
        return record.html_preview

    async def delete_resume(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> None:
        """Delete all resume versions for a job."""
        result = await db.execute(
            select(ResumeVersion).where(
                ResumeVersion.user_id == user_id,
                ResumeVersion.job_id == job_id,
            )
        )
        records = result.scalars().all()
        if not records:
            raise HTTPException(status_code=404, detail="No resume versions found")
        for r in records:
            await db.delete(r)
        await db.commit()

    @staticmethod
    def _generate_html(
        user_name: str, sections: ResumeSections, profile: UserProfile
    ) -> str:
        """Generate a professional HTML resume."""
        # Contact info
        contact_parts = []
        if profile.school:
            contact_parts.append(profile.school)
        if profile.major:
            contact_parts.append(profile.major)
        if profile.grade:
            contact_parts.append(profile.grade)
        contact_line = " | ".join(contact_parts)

        # Summary
        summary_content = sections.summary.get("content", "") if sections.summary else ""
        summary_html = f'<p class="summary-text">{summary_content}</p>' if summary_content else ""

        # Job intention
        job_intention_content = sections.job_intention.get("content", "") if sections.job_intention else ""
        job_intention_html = f'<div class="section"><h2>求职意向</h2><p class="summary-text">{job_intention_content}</p></div>' if job_intention_content else ""

        # Skills
        skills_list = []
        skill_changes = []
        if sections.skills:
            skills_list = sections.skills.get("content", [])
            skill_changes_raw = sections.skills.get("changes", [])
            for sc in skill_changes_raw:
                if hasattr(sc, "model_dump"):
                    skill_changes.append(sc.model_dump())
                else:
                    skill_changes.append(sc)

        skills_html = ""
        if skills_list:
            tags = "".join(
                f'<span class="skill-tag">{s}</span>' for s in skills_list
            )
            skills_html = f'<div class="skills-grid">{tags}</div>'

        # Skill changes table
        skill_changes_html = ""
        if skill_changes:
            rows = ""
            for sc in skill_changes:
                rows += f"<tr><td>{sc.get('skill','')}</td><td>{sc.get('action','')}</td><td>{sc.get('reason','')}</td></tr>"
            skill_changes_html = f"""
            <div class="section">
                <h2>技能变更记录</h2>
                <table class="changes-table">
                    <thead><tr><th>技能</th><th>操作</th><th>原因</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>"""

        # Experience
        experience_html = ""
        if sections.experiences:
            items = ""
            for exp in sections.experiences:
                rewritten = exp.rewritten if hasattr(exp, "rewritten") else str(exp)
                changes_list = ""
                if hasattr(exp, "changes") and exp.changes:
                    changes_list = "".join(f"<li>{c}</li>" for c in exp.changes)
                changes_block = f'<ul class="changes-list">{changes_list}</ul>' if changes_list else ""
                items += f"""
                <div class="experience-item">
                    <div class="exp-rewritten">{rewritten}</div>
                    {changes_block}
                </div>"""
            experience_html = f'<div class="section"><h2>工作/实习经历</h2>{items}</div>'

        # Education (from profile)
        education_html = ""
        if profile.resume_structured and profile.resume_structured.get("education"):
            items = ""
            for edu in profile.resume_structured["education"]:
                school = edu.get("school", "")
                major = edu.get("major", "")
                degree = edu.get("degree", "")
                period = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
                edu_line = " | ".join(filter(None, [school, major, degree, period]))
                items += f'<div class="education-item">{edu_line}</div>'
            education_html = f'<div class="section"><h2>教育背景</h2>{items}</div>'

        # Full HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{user_name} - 定制简历</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        color: #1e293b;
        line-height: 1.6;
        background: #fff;
    }}
    .resume-container {{
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
    }}
    .header {{
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #2563eb;
        margin-bottom: 24px;
    }}
    .header h1 {{
        font-size: 28px;
        color: #2563eb;
        margin-bottom: 8px;
    }}
    .header .contact-info {{
        font-size: 14px;
        color: #64748b;
    }}
    .section {{
        margin-bottom: 24px;
    }}
    .section h2 {{
        font-size: 18px;
        color: #2563eb;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }}
    .summary-text {{
        font-size: 15px;
        color: #334155;
        line-height: 1.8;
    }}
    .skills-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }}
    .skill-tag {{
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 13px;
        border: 1px solid #bfdbfe;
    }}
    .experience-item {{
        margin-bottom: 16px;
        padding: 12px;
        background: #f8fafc;
        border-radius: 6px;
        border-left: 3px solid #2563eb;
    }}
    .exp-rewritten {{
        font-size: 14px;
        color: #334155;
        line-height: 1.7;
        white-space: pre-wrap;
    }}
    .changes-list {{
        margin-top: 8px;
        padding-left: 20px;
        font-size: 13px;
        color: #64748b;
    }}
    .education-item {{
        padding: 8px 0;
        font-size: 14px;
        border-bottom: 1px dashed #e2e8f0;
    }}
    .changes-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }}
    .changes-table th, .changes-table td {{
        border: 1px solid #e2e8f0;
        padding: 6px 10px;
        text-align: left;
    }}
    .changes-table th {{
        background: #f1f5f9;
        color: #475569;
        font-weight: 600;
    }}
    @media print {{
        body {{ font-size: 12pt; }}
        .resume-container {{ padding: 20px; max-width: 100%; }}
        .header h1 {{ font-size: 24pt; }}
        .section h2 {{ font-size: 14pt; }}
        .skill-tag {{ border: 1px solid #999; }}
        .experience-item {{ break-inside: avoid; }}
        @page {{ size: A4; margin: 15mm; }}
    }}
</style>
</head>
<body>
<div class="resume-container">
    <div class="header">
        <h1>{user_name}</h1>
        <div class="contact-info">{contact_line}</div>
    </div>
    {job_intention_html}
    {summary_html}
    {education_html}
    {skills_html}
    {skill_changes_html}
    {experience_html}
</div>
</body>
</html>"""
        return html

    @staticmethod
    def _to_response(record: ResumeVersion) -> ResumeRewriteResponse:
        sections = None
        if record.sections:
            sections = ResumeSections.model_validate(record.sections)
        return ResumeRewriteResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            version=record.version,
            sections=sections,
            html_preview=record.html_preview,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    async def _get_profile(db: AsyncSession, user_id: str) -> UserProfile:
        result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile

    @staticmethod
    async def _get_job(db: AsyncSession, job_id: str) -> JobPost:
        result = await db.execute(select(JobPost).where(JobPost.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job post not found")
        return job


resume_service = ResumeService()
