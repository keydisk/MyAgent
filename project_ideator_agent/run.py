"""PaceSnap(PhotoAndActivitiesApp) 프로젝트 개선 아이디어 분석 및 리포트 실행 스크립트"""

import sys
import argparse
from project_ideator_agent.project_analyzer import scan_project_structure
from project_ideator_agent.idea_generator import generate_daily_ideas
from project_ideator_agent.pdf_generator import build_pdf_report
from project_ideator_agent.ideator_ui import show_ideator_window

def run_project_ideator(no_gui: bool = False) -> str:
    print("=" * 65)
    print("🚀 [ProjectIdeator] PaceSnap 프로젝트 개선 탐색 및 리포트 시작")
    print("=" * 65)

    # 1. 대상 프로젝트 분석
    print("[*] 1단계: /Users/juyoungchoi/Documents/Project/PhotoAndActivitiesApp 분석 중...")
    project_info = scan_project_structure()
    print(f"    - 감지된 주요 피처: {', '.join(project_info.get('features', []))}")
    print(f"    - 발견된 이슈/포인트: {len(project_info.get('key_findings', []))}건")

    # 2. 아이디어 생성
    print("[*] 2단계: 최신 러닝 트렌드 및 기술 기반 혁신 아이디어 5선 도출 중...")
    report_data = generate_daily_ideas(project_info)

    # 3. PDF 리포트 빌드
    print("[*] 3단계: 애플 스타일 A4 고품질 PDF 리포트 렌더링 중...")
    pdf_path = build_pdf_report(report_data)

    # 4. 결과 창 표시 및 지시 입력 인터페이스
    if not no_gui:
        print(f"[*] 4단계: PDF 창 및 에이전트 지시 콘솔을 엽니다...")
        show_ideator_window(pdf_path, report_data)
    else:
        print(f"[✓] 완료! PDF가 생성되었습니다: {pdf_path}")

    return pdf_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PaceSnap 프로젝트 개선 아이디어 리포터")
    parser.add_argument("--no-gui", action="store_true", help="UI 창을 열지 않고 PDF만 생성")
    args = parser.parse_args()

    run_project_ideator(no_gui=args.no_gui)
