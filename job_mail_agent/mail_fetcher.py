"""AppleScript를 이용해 macOS Mail.app에서 채용 관련 메일을 수집하는 모듈.
"""

import subprocess
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# 채용 관련 키워드 목록
JOB_KEYWORDS = [
    # 한국어 키워드
    "채용", "공고", "모집", "포지션", "인재", "서류", "면접", "합격", "불합격",
    "이력서", "헤드헌터", "이직", "구인", "경력직", "신입", "인턴", "오퍼",
    "사람인", "원티드", "잡코리아", "링크드인", "리멤버", "플렉스웍", "이랜서", "로켓펀치",
    # 영어 키워드
    "recruit", "recruiting", "recruitment", "recruiter", "hiring", "hire",
    "job", "jobs", "career", "careers", "position", "opening", "offer",
    "interview", "application", "applicant", "candidate"
]

def is_job_related(text: str) -> bool:
    """텍스트(제목, 발신자, 본문 등)에 채용 관련 키워드가 포함되어 있는지 검사"""
    if not text:
        return False
    lower_text = text.lower()
    return any(keyword.lower() in lower_text for keyword in JOB_KEYWORDS)

def run_applescript(script: str) -> str:
    """AppleScript를 실행하고 stdout 결과를 반환"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[오류] AppleScript 실행 실패: {e.stderr}")
        return ""

def fetch_recent_emails(limit: int = 30) -> List[Dict[str, Any]]:
    """
    Mail.app의 받은편지함(Inbox)에서 최근 메일 목록을 가져온 뒤
    채용 관련 메일만 필터링하여 상세 내용(본문 등)을 조회합니다.
    """
    print(f"[*] Mail.app 받은편지함에서 최근 {limit}개의 메일을 스캔합니다...")

    # 1단계: 최근 메일 메타데이터(제목, 발신자, 날짜, 인덱스) 목록 가져오기
    # 구분자 '|||ITEM|||' 및 '|||FIELD|||' 사용
    script_list = f"""
    tell application "Mail"
        set totalCount to count of messages of inbox
        set maxCount to {limit}
        if totalCount < maxCount then
            set maxCount to totalCount
        end if
        
        set output to ""
        repeat with i from 1 to maxCount
            try
                set msg to message i of inbox
                set sSubject to subject of msg
                set sSender to sender of msg
                set sDate to date received of msg as string
                set output to output & i & "|||FIELD|||" & sSubject & "|||FIELD|||" & sSender & "|||FIELD|||" & sDate & "|||ITEM|||"
            end try
        end repeat
        return output
    end tell
    """

    raw_output = run_applescript(script_list)
    if not raw_output:
        print("[!] 메일을 가져올 수 없거나 받은편지함이 비어 있습니다.")
        return []

    items = [item.strip() for item in raw_output.split("|||ITEM|||") if item.strip()]
    candidate_indices = []
    
    # 1차 필터링: 제목 또는 발신자에서 채용 키워드 감지
    for item in items:
        fields = item.split("|||FIELD|||")
        if len(fields) >= 4:
            idx = int(fields[0])
            subject = fields[1]
            sender = fields[2]
            date_str = fields[3]
            
            # 제목이나 발신자에 키워드가 있는지 확인
            if is_job_related(subject) or is_job_related(sender):
                candidate_indices.append((idx, subject, sender, date_str, True))
            else:
                # 제목에 명시되지 않아도 본문 검사를 위해 일부 최근 메일도 후보군에 포함
                candidate_indices.append((idx, subject, sender, date_str, False))

    print(f"[*] 총 {len(items)}개 메일 중 채용 유력/후보 메일 상세 본문 분석 중...")

    job_emails = []

    # 2단계: 후보 메일들의 본문 및 원문 소스(URL 포함) 가져오기
    for idx, subject, sender, date_str, title_matched in candidate_indices:
        # 이미 제목에서 매칭되었거나, 최근 15개 이내면 본문까지 확인
        if not title_matched and idx > 15:
            continue

        detail_script = f"""
        tell application "Mail"
            try
                set msg to message {idx} of inbox
                set bContent to content of msg
                set bSource to source of msg
                return bContent & "|||CONTENT_SOURCE_SEP|||" & bSource
            on error
                return ""
            end try
        end tell
        """
        detail_raw = run_applescript(detail_script)
        if not detail_raw:
            continue

        parts = detail_raw.split("|||CONTENT_SOURCE_SEP|||")
        content = parts[0] if len(parts) > 0 else ""
        source = parts[1] if len(parts) > 1 else ""

        # 제목 또는 본문에서 채용 키워드가 확인되면 추가
        if title_matched or is_job_related(content):
            job_emails.append({
                "index": idx,
                "subject": subject,
                "sender": sender,
                "date": date_str,
                "content": content,
                "source": source
            })

    print(f"[✓] 채용 관련 메일 총 {len(job_emails)}건 발견!")
    return job_emails
