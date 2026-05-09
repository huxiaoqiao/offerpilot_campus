"""Prompts package - LLM prompt templates."""

from app.prompts.jd_extract import build_jd_extract_messages
from app.prompts.resume_extract import build_resume_extract_messages
from app.prompts.match_score import build_match_messages
from app.prompts.resume_rewrite import build_rewrite_messages
from app.prompts.hr_simulate import build_hr_messages
from app.prompts.interview_gen import build_interview_messages

__all__ = [
    "build_jd_extract_messages",
    "build_resume_extract_messages",
    "build_match_messages",
    "build_rewrite_messages",
    "build_hr_messages",
    "build_interview_messages",
]
