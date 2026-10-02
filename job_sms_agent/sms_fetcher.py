"""macOS Messages.app (chat.db)에서 최근 수신 문자를 조회하고
구직/일/채용 관련 문자를 필터링하는 모듈.
"""

import os
import sqlite3
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Tuple

CHAT_DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")

SMS_JOB_KEYWORDS = [
    # 구직 및 채용 키워드
    "구직", "채용", "일자리", "면접", "서류", "합격", "불합격", "이력서",
    "지원", "제안", "프로젝트", "외주", "개발자", "구인", "포지션",
    "인사담당", "헤드헌터", "사람인", "잡코리아", "원티드", "알바",
    "급여", "프리랜서", "오퍼", "인턴", "계약직", "정규직", "근무", "출근",
    "과제", "코딩테스트", "테스트", "평가",
    # 영어 키워드
    "job", "career", "hiring", "recruit", "recruiter", "offer",
    "interview", "freelance", "position", "applicant"
]

def check_chat_db_permission() -> Tuple[bool, str]:
    """chat.db 접근 권한(Full Disk Access) 확인"""
    if not os.path.exists(CHAT_DB_PATH):
        return False, f"Messages 데이터베이스 파일을 찾을 수 없습니다: {CHAT_DB_PATH}"

    try:
        conn = sqlite3.connect(f"file:{CHAT_DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM message LIMIT 1;")
        cursor.fetchone()
        conn.close()
        return True, "정상 접근 가능"
    except sqlite3.OperationalError as e:
        if "authorization denied" in str(e).lower() or "unable to open" in str(e).lower():
            return False, "Full Disk Access(전체 디스크 접근 권한)가 필요합니다."
        return False, str(e)
    except Exception as e:
        return False, str(e)

def open_privacy_settings():
    """macOS 개인정보 보호 및 보안 > 전체 디스크 접근 권한 설정 창 열기"""
    subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"])

def is_job_or_work_related(text: str) -> bool:
    """텍스트가 구직/일/채용 관련인지 판별"""
    if not text:
        return False
    lower = text.lower()
    return any(k.lower() in lower for k in SMS_JOB_KEYWORDS)

def fetch_recent_sms_messages(limit: int = 100) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    최근 수신된 SMS/iMessage 중 구직/일 관련 문자들을 추출합니다.
    반환값: (메시지 리스트, 권한 정상 여부, 상태 메시지)
    """
    has_perm, msg = check_chat_db_permission()
    if not has_perm:
        return [], False, msg

    query = """
    SELECT
        m.rowid,
        COALESCE(h.id, '알 수 없음') as sender_id,
        datetime(m.date / 1000000000 + 978307200, 'unixepoch', 'localtime') as msg_date,
        m.text,
        m.service
    FROM message m
    LEFT JOIN handle h ON m.handle_id = h.rowid
    WHERE m.is_from_me = 0
      AND m.text IS NOT NULL
      AND length(trim(m.text)) > 0
    ORDER BY m.date DESC
    LIMIT ?;
    """

    results = []
    try:
        conn = sqlite3.connect(f"file:{CHAT_DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()

        for rowid, sender, date_str, text, service in rows:
            if is_job_or_work_related(text):
                results.append({
                    "id": rowid,
                    "sender": sender,
                    "date": date_str,
                    "text": text,
                    "service": service or "SMS/iMessage"
                })

        return results, True, f"총 {len(rows)}개 문자 중 구직/일 관련 문자 {len(results)}건 발견"
    except Exception as e:
        return [], False, f"데이터베이스 조회 오류: {str(e)}"
