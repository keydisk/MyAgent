"""채용 메일 확인 및 요약 창 실행 스크립트"""

import sys
import argparse
from job_mail_agent.mail_fetcher import fetch_recent_emails
from job_mail_agent.mail_analyzer import summarize_job_email
from job_mail_agent.mail_ui import show_job_emails_ui

def run_job_mail_agent(limit: int = 30, no_gui: bool = False):
    print("=" * 60)
    print("🚀 [JobMailAgent] macOS 채용 메일 탐지 및 요약 에이전트 시작")
    print("=" * 60)
    
    # 1. 메일 수집
    raw_emails = fetch_recent_emails(limit=limit)
    if not raw_emails:
        print("\n[!] 최근 채용 관련 메일이 없습니다.")
        if not no_gui:
            show_job_emails_ui([])
        return []

    # 2. 메일 분석 및 링크 스크랩 요약
    summarized_list = []
    print(f"\n[*] 발견된 {len(raw_emails)}건의 채용 메일을 분석하고 링크를 크롤링합니다...")
    for idx, em in enumerate(raw_emails, start=1):
        print(f"  [{idx}/{len(raw_emails)}] '{em['subject'][:30]}...' 분석 중...")
        summary = summarize_job_email(em)
        summarized_list.append(summary)

    print("\n[✓] 모든 메일 및 링크 분석 완료!")
    
    # 3. GUI 창 띄우기
    if not no_gui:
        print("[*] 요약 결과 GUI 창을 엽니다...")
        show_job_emails_ui(summarized_list)
    else:
        print("\n[콘솔 출력 모드]")
        for s in summarized_list:
            print(f"- 제목: {s['subject']}")
            print(f"  발신자: {s['sender']} | 수신일: {s['date']}")
            print(f"  요약: {s['job_summary'][:150]}...")
            print(f"  링크 수: {len(s['links'])}")

    return summarized_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="macOS 채용 메일 모니터링 & 요약")
    parser.add_argument("--limit", type=int, default=30, help="스캔할 최근 메일 개수 (기본: 30)")
    parser.add_argument("--no-gui", action="store_true", help="GUI 창을 띄우지 않고 콘솔에만 출력")
    args = parser.parse_args()
    
    run_job_mail_agent(limit=args.limit, no_gui=args.no_gui)
