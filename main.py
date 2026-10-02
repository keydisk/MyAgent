#!/usr/bin/env python3
"""
MyAgent 통합 오케스트레이터 & 확장 가능한 메인 실행기.

하위 모듈들을 레지스트리 패턴으로 관리하여 추후 새로운 기능/에이전트 폴더가 추가되더라도
손쉽게 기능을 확장할 수 있습니다.
"""

import sys
import os
import argparse
from typing import Callable, Dict, Any

# 루트 디렉터리를 sys.path에 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# 모듈별 기능 임포트
from job_mail_agent.run import run_job_mail_agent
from project_ideator_agent.run import run_project_ideator
from project_ideator_agent.schedule_manager import (
    install_launchd_schedule,
    uninstall_launchd_schedule,
    check_schedule_status
)
from github_manager.git_service import sync_and_push_repo, commit_changes

# -------------------------------------------------------------
# 확장 가능한 명령어 레지스트리 (Command Registry)
# -------------------------------------------------------------
AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {}

def register_command(name: str, handler: Callable, description: str, category: str = "일반"):
    """새로운 서브 에이전트/기능을 등록하는 확장 인터페이스"""
    AGENT_REGISTRY[name] = {
        "handler": handler,
        "description": description,
        "category": category
    }

# -------------------------------------------------------------
# 명령어 핸들러 정의
# -------------------------------------------------------------
def cmd_check_mail(args):
    """채용 메일 및 링크 요약 창 띄우기"""
    limit = getattr(args, 'limit', 30)
    no_gui = getattr(args, 'no_gui', False)
    run_job_mail_agent(limit=limit, no_gui=no_gui)

def cmd_ideate(args):
    """PhotoAndActivitiesApp 개선 아이디어 리포트 PDF 생성 및 지시 창"""
    no_gui = getattr(args, 'no_gui', False)
    run_project_ideator(no_gui=no_gui)

def cmd_schedule(args):
    """평일 오전 11시 스케줄 관리"""
    action = getattr(args, 'action', 'status')
    if action == 'install':
        success, msg = install_launchd_schedule()
        print(f"\n[스케줄 등록] {'성공' if success else '실패'}\n{msg}")
    elif action == 'uninstall':
        success, msg = uninstall_launchd_schedule()
        print(f"\n[스케줄 해제] {msg}")
    else:
        print("\n" + check_schedule_status())

def cmd_sync_github(args):
    """GitHub 저장소 생성 및 푸시"""
    repo_name = getattr(args, 'repo', 'MyAgent')
    is_private = getattr(args, 'private', False)
    print(f"\n[*] GitHub 저장소({repo_name})와 동기화 및 푸시를 진행합니다...")
    success, msg = sync_and_push_repo(repo_name=repo_name, is_private=is_private)
    print(f"\n[결과] {'성공 ✓' if success else '실패 ✗'}\n{msg}")

def cmd_all(args):
    """모든 주요 기능 일괄 순차 실행"""
    print("\n[1/2] 채용 관련 메일 스캔 및 요약 창 실행")
    cmd_check_mail(args)
    print("\n[2/2] PhotoAndActivitiesApp 아이디어 PDF 생성 및 지시 창 실행")
    cmd_ideate(args)

# -------------------------------------------------------------
# 기능 등록 (여기에 신규 모듈을 한 줄씩 추가하여 확장 가능)
# -------------------------------------------------------------
register_command(
    name="check-mail",
    handler=cmd_check_mail,
    description="macOS Mail.app에서 채용 관련 메일 및 링크를 스캔하여 요약 창 띄우기",
    category="메일 모니터링"
)

register_command(
    name="ideate",
    handler=cmd_ideate,
    description="PhotoAndActivitiesApp 개선 아이디어 탐색, PDF 생성, 창 띄우기 및 사용자 지시 콘솔",
    category="프로젝트 아이디어"
)

register_command(
    name="schedule-ideator",
    handler=cmd_schedule,
    description="평일 오전 11시 아이디어 리포트 자동 생성 스케줄러 관리 (launchd)",
    category="스케줄링"
)

register_command(
    name="sync-github",
    handler=cmd_sync_github,
    description="수정된 코드를 로컬 git 커밋 및 사용자 GitHub 저장소에 푸시",
    category="GitHub 연동"
)

register_command(
    name="all",
    handler=cmd_all,
    description="채용 메일 확인 및 프로젝트 아이디어 리포트 연속 실행",
    category="전체 실행"
)

# -------------------------------------------------------------
# 인터랙티브 런처 메뉴
# -------------------------------------------------------------
def run_interactive_menu():
    """인자가 주어지지 않았을 때 대화형 메뉴 제공"""
    print("\n" + "=" * 65)
    print("🤖 MyAgent 종합 제어 센터 (Mac Autonomous Agent)")
    print("=" * 65)
    
    commands = list(AGENT_REGISTRY.keys())
    for idx, cmd_name in enumerate(commands, start=1):
        item = AGENT_REGISTRY[cmd_name]
        print(f" [{idx}] {cmd_name:<18} : {item['description']} ({item['category']})")
    print(" [0] 종료 (Exit)")
    print("=" * 65)
    
    try:
        choice = input("👉 실행할 기능의 번호를 입력하세요 (0~5): ").strip()
        if choice == "0":
            print("프로그램을 종료합니다.")
            return
        
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(commands):
            selected_cmd = commands[choice_idx]
            print(f"\n[*] '{selected_cmd}' 실행을 시작합니다...\n")
            
            # 기본 빈 Namespace 객체 생성
            empty_args = argparse.Namespace(limit=30, no_gui=False, action='status', repo='MyAgent', private=False)
            AGENT_REGISTRY[selected_cmd]["handler"](empty_args)
        else:
            print("[!] 올바른 번호를 입력해주세요.")
    except (ValueError, KeyboardInterrupt):
        print("\n실행이 취소되었습니다.")

# -------------------------------------------------------------
# CLI 메인 진입점
# -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="MyAgent: 채용 메일 요약 및 PhotoAndActivitiesApp 일일 개선 리포트 에이전트",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="실행할 하위 명령어를 선택하세요")

    # 1. check-mail
    p_mail = subparsers.add_parser("check-mail", help=AGENT_REGISTRY["check-mail"]["description"])
    p_mail.add_argument("--limit", type=int, default=30, help="스캔할 최근 메일 개수 (기본: 30)")
    p_mail.add_argument("--no-gui", action="store_true", help="GUI 창을 띄우지 않고 콘솔에만 출력")

    # 2. ideate
    p_ideate = subparsers.add_parser("ideate", help=AGENT_REGISTRY["ideate"]["description"])
    p_ideate.add_argument("--no-gui", action="store_true", help="UI 창을 띄우지 않고 PDF만 생성")

    # 3. schedule-ideator
    p_sched = subparsers.add_parser("schedule-ideator", help=AGENT_REGISTRY["schedule-ideator"]["description"])
    p_sched.add_argument("action", nargs="?", default="status", choices=["status", "install", "uninstall"],
                         help="스케줄 동작: status(상태확인), install(평일 오전 11시 등록), uninstall(해제)")

    # 4. sync-github
    p_git = subparsers.add_parser("sync-github", help=AGENT_REGISTRY["sync-github"]["description"])
    p_git.add_argument("--repo", default="MyAgent", help="GitHub 저장소 이름 (기본: MyAgent)")
    p_git.add_argument("--private", action="store_true", help="비공개 저장소로 생성")

    # 5. all
    p_all = subparsers.add_parser("all", help=AGENT_REGISTRY["all"]["description"])
    p_all.add_argument("--limit", type=int, default=30, help="스캔할 최근 메일 개수")
    p_all.add_argument("--no-gui", action="store_true", help="GUI 창 생략")

    args = parser.parse_args()

    if args.command is None:
        run_interactive_menu()
    else:
        cmd_info = AGENT_REGISTRY.get(args.command)
        if cmd_info:
            cmd_info["handler"](args)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
