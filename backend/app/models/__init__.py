"""Re-export all ORM models so that `import app.models` registers them on Base.metadata."""

from app.models.application import Application
from app.models.hr import HRSimulation
from app.models.interview import InterviewSet
from app.models.job import JobPost
from app.models.match import MatchResult
from app.models.profile import UserProfile
from app.models.resume import ResumeVersion

__all__ = [
    "Application",
    "HRSimulation",
    "InterviewSet",
    "JobPost",
    "MatchResult",
    "UserProfile",
    "ResumeVersion",
]
