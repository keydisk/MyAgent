"""구직 및 업무 관련 문자 요약 실행 스크립트"""

import sys
import argparse
from job_sms_agent.sms_fetcher import fetch_recent_sms_messages, check_chat_db_permission
from job_sms_agent.sms_analyzer import summarize_sms
from job_sms_agent.sms_ui import show_sms_ui

def run_job_sms_agent(limit: int = 100, no_gui: bool = False):
    print("=" * 65)
    print("🚀 [JobSMSAgent] macOS 구직 & 업무 관련 문자 요약 에이전트 시작")
    print("=" * 65)

    has_perm, perm_msg = check_chat_db_permission()
    if not has_perm:
        print(f"\n[⚠️ 권한 필요] {perm_msg}")
        print("macOS 개인정보 보호 정책으로 인해 터미널에 '전체 디스크 접근 권한'이 필요합니다.")
        print("설정 앱: 시스템 설정 > 개인정보 보호 및 보안 > 전체 디스크 접근 권한")
        if not no_gui:
            show_sms_ui([], has_permission=False, perm_msg=perm_msg)
        return []

    # 문자 수집
    raw_msgs, ok, status_str = fetch_recent_sms_messages(limit=limit)
    print(f"[*] {status_str}")

    if not raw_msgs:
        print("[!] 최근 수신된 구직/업무 관련 문자가 없습니다.")
        if not no_gui:
            show_sms_ui([], has_permission=True)
        return []

    # 문자 분석 및 Gemini 3.8 Flash High 요약
    summarized_list = []
    print(f"[*] 발견된 {len(raw_msgs)}건의 문자를 AI(Gemini 3.8 Flash High)로 분석/요약 중...")
    for idx, msg in enumerate(raw_msgs, start=1):
        print(f"  [{idx}/{len(raw_msgs)}] 발신자: {msg['sender']} 요약 중...")
        s = summarize_sms(msg)
        summarized_list.append(s)

    print("[✓] 모든 문자 분석 완료!")

    if not no_gui:
        print("[*] 문자 요약 GUI 창을 엽니다...")
        show_sms_ui(summarized_list, has_permission=True)
    else:
        for s in summarized_list:
            print(f"- 발신자: {s['sender']} | {s['date']}")
            print(f"  요약: {s['summary']}")

    return summarized_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="macOS 구직 & 업무 문자 요약")
    parser.add_argument("--limit", type=int, default=100, help="스캔할 최근 문자 개수 (기본: 100)")
    parser.add_argument("--no-gui", action="store_true", help="GUI 창을 띄우지 않고 콘솔에만 출력")
    args = parser.parse_args()

    run_job_sms_agent(limit=args.limit, no_gui=args.no_gui)
