"""JobService - business logic for job post operations."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobPost
from app.parser.jd_parser import jd_parser
from app.schemas.job import JobCreate, JobResponse
from app.schemas.common import PaginatedResponse
from app.utils.id_utils import gen_id
from app.utils.text_utils import similarity

logger = logging.getLogger(__name__)

DEDUP_THRESHOLD = 0.8


class JobService:
    """Async service layer for job post CRUD and JD parsing."""

    async def create_job(self, db: AsyncSession, user_id: str, job_data: JobCreate) -> JobPost:
        """Parse a JD and create a job post record."""
        extracted = await jd_parser.parse_jd(job_data.jd_raw_text)

        # Check for duplicates against existing jobs for this user
        is_dup, dup_of = await self._check_duplicate(
            db, user_id,
            job_data.position_title or extracted.position_title or "",
            job_data.company_name or extracted.company_name or "",
        )

        job = JobPost(
            id=gen_id(),
            user_id=user_id,
            company_name=job_data.company_name or extracted.company_name,
            position_title=job_data.position_title or extracted.position_title,
            jd_raw_text=job_data.jd_raw_text,
            responsibilities=extracted.responsibilities,
            hard_requirements=extracted.hard_requirements,
            soft_requirements=extracted.soft_requirements,
            salary_min=extracted.salary_min,
            salary_max=extracted.salary_max,
            city=extracted.city,
            industry=extracted.industry,
            keywords=extracted.keywords,
            source_url=job_data.source_url,
            quality_score=extracted.quality_score,
            quality_details=extracted.quality_details.model_dump(),
            risk_tags=extracted.risk_tags,
            is_duplicate=is_dup,
            duplicate_of=dup_of,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    async def create_jobs_batch(
        self, db: AsyncSession, user_id: str, jobs_data: list[JobCreate]
    ) -> list[JobPost]:
        """Parse and create multiple job posts."""
        results = []
        for job_data in jobs_data:
            job = await self.create_job(db, user_id, job_data)
            results.append(job)
        return results

    async def import_csv(self, db: AsyncSession, user_id: str, file_path: str) -> list[JobPost]:
        """Import jobs from a CSV file.

        Expected columns: company_name, position_title, jd_raw_text, source_url (optional)
        """
        results = []
        p = Path(file_path)
        with p.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                jd_text = row.get("jd_raw_text", "").strip()
                if not jd_text or len(jd_text) < 10:
                    continue
                job_data = JobCreate(
                    company_name=row.get("company_name", "").strip() or None,
                    position_title=row.get("position_title", "").strip() or None,
                    jd_raw_text=jd_text,
                    source_url=row.get("source_url", "").strip() or None,
                )
                job = await self.create_job(db, user_id, job_data)
                results.append(job)
        return results

    async def get_jobs(
        self,
        db: AsyncSession,
        user_id: str,
        sort_by: str = "created_at",
        order: str = "desc",
        city: str | None = None,
        industry: str | None = None,
        min_score: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[JobResponse]:
        """Get paginated, filtered job list."""
        query = select(JobPost).where(JobPost.user_id == user_id)
        count_query = select(func.count()).select_from(JobPost).where(JobPost.user_id == user_id)

        if city:
            query = query.where(JobPost.city == city)
            count_query = count_query.where(JobPost.city == city)
        if industry:
            query = query.where(JobPost.industry == industry)
            count_query = count_query.where(JobPost.industry == industry)
        if min_score is not None:
            query = query.where(JobPost.quality_score >= min_score)
            count_query = count_query.where(JobPost.quality_score >= min_score)

        # Sorting
        sort_column = getattr(JobPost, sort_by, JobPost.created_at)
        if order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        result = await db.execute(query)
        jobs = result.scalars().all()

        return PaginatedResponse(
            data=[JobResponse.model_validate(j) for j in jobs],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_job(self, db: AsyncSession, job_id: str) -> JobPost | None:
        """Get a single job by ID."""
        result = await db.execute(select(JobPost).where(JobPost.id == job_id))
        return result.scalar_one_or_none()

    async def delete_job(self, db: AsyncSession, job_id: str) -> None:
        """Delete a job post."""
        result = await db.execute(select(JobPost).where(JobPost.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        await db.delete(job)
        await db.commit()

    async def reparse_job(self, db: AsyncSession, job_id: str) -> JobPost:
        """Re-parse a job's raw JD text using LLM."""
        result = await db.execute(select(JobPost).where(JobPost.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        if not job.jd_raw_text:
            raise ValueError("No raw JD text to reparse")

        extracted = await jd_parser.parse_jd(job.jd_raw_text)
        job.company_name = extracted.company_name
        job.position_title = extracted.position_title
        job.responsibilities = extracted.responsibilities
        job.hard_requirements = extracted.hard_requirements
        job.soft_requirements = extracted.soft_requirements
        job.salary_min = extracted.salary_min
        job.salary_max = extracted.salary_max
        job.city = extracted.city
        job.industry = extracted.industry
        job.keywords = extracted.keywords
        job.quality_score = extracted.quality_score
        job.quality_details = extracted.quality_details.model_dump()
        job.risk_tags = extracted.risk_tags

        await db.commit()
        await db.refresh(job)
        return job

    async def _check_duplicate(
        self, db: AsyncSession, user_id: str, title: str, company: str
    ) -> tuple[bool, str | None]:
        """Check if a similar job already exists for this user."""
        if not title and not company:
            return False, None

        result = await db.execute(
            select(JobPost).where(
                JobPost.user_id == user_id,
                JobPost.is_duplicate == False,  # noqa: E712
            )
        )
        existing_jobs = result.scalars().all()

        for existing in existing_jobs:
            existing_title = existing.position_title or ""
            existing_company = existing.company_name or ""
            title_sim = similarity(title, existing_title)
            company_sim = similarity(company, existing_company)
            # Both title and company must be similar
            if title_sim > DEDUP_THRESHOLD and company_sim > DEDUP_THRESHOLD:
                return True, existing.id
        return False, None


# Module-level singleton
job_service = JobService()
