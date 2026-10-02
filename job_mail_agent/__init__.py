"""job_mail_agent 패키지 초기화"""
from .mail_fetcher import fetch_recent_emails
from .mail_analyzer import summarize_job_email
from .mail_ui import show_job_emails_ui

__all__ = ["fetch_recent_emails", "summarize_job_email", "show_job_emails_ui"]
