"""구직/일 관련 수신 문자를 분석하고 요약하는 모듈.
Gemini 3.8 Flash High(설정 시) 또는 지능형 로컬 요약기를 활용합니다.
"""

import re
from typing import Dict, Any, List
from common.gemini_client import summarize_text_with_gemini
from job_mail_agent.mail_analyzer import extract_urls, fetch_and_summarize_url

def summarize_sms(msg_data: Dict[str, Any]) -> Dict[str, Any]:
    """문자 내용 요약 및 포함된 링크 분석"""
    text = msg_data.get("text", "")
    sender = msg_data.get("sender", "")
    date_str = msg_data.get("date", "")
    service = msg_data.get("service", "")

    # 1. 커리어 가이드 적합도 판정
    from common.career_profile import evaluate_job_match, get_career_summary_for_prompt
    fit_eval = evaluate_job_match(title=text[:40], company=sender, content=text)

    # 2. Gemini 3.8 Flash High 요약 시도
    ai_summary = summarize_text_with_gemini(
        f"{get_career_summary_for_prompt()}\n\n[수신 문자]\n{text}",
        context_type="구직/채용 및 외주 업무"
    )

    # AI 요약이 없으면 로컬 휴리스틱 요약 생성
    if not ai_summary:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        key_lines = []
        for line in lines:
            if any(k in line for k in ["채용", "면접", "합격", "프로젝트", "외주", "지원", "서류", "일정", "제안", "급여"]):
                key_lines.append(f"• {line}")
        if key_lines:
            summary_text = "\n".join(key_lines[:4])
        else:
            summary_text = f"• {lines[0] if lines else '내용 없음'}"
    else:
        summary_text = ai_summary

    # 3. 링크 추출 및 스크랩
    urls = extract_urls(text)
    link_summaries = []
    for u in urls[:2]:
        link_summaries.append(fetch_and_summarize_url(u))

    return {
        "id": msg_data.get("id"),
        "sender": sender,
        "date": date_str,
        "service": service,
        "summary": summary_text,
        "fit_eval": fit_eval,
        "raw_text": text,
        "links": link_summaries
    }
