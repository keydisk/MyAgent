"""PaceSnap(PhotoAndActivitiesApp) 프로젝트 분석 모듈.
대상 프로젝트의 파일 구조, 소스 코드, 기획서, 아키텍처 문서를 분석하여
현재 상태와 개선 가능 영역을 도출합니다.
"""

import os
import re
from typing import Dict, Any, List

TARGET_PROJECT_PATH = "/Users/juyoungchoi/Documents/Project/PhotoAndActivitiesApp"

def scan_project_structure(base_path: str = TARGET_PROJECT_PATH) -> Dict[str, Any]:
    """대상 프로젝트 디렉터리 구조 및 핵심 파일 스캔"""
    if not os.path.exists(base_path):
        return {"error": f"프로젝트 경로를 찾을 수 없습니다: {base_path}"}

    summary = {
        "project_name": "PaceSnap (PhotoAndActivitiesApp)",
        "path": base_path,
        "exists": True,
        "modules": [],
        "documents": [],
        "features": [],
        "key_findings": []
    }

    # 1. 문서 파일 탐색
    for root, dirs, files in os.walk(base_path):
        # 불필요한 디렉터리 건너뛰기
        dirs[:] = [d for d in dirs if d not in ['.git', '.claude', 'Tuist/.build', 'DerivedData']]
        for f in files:
            if f.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, f), base_path)
                summary["documents"].append(rel_path)

    # 2. 모듈 및 피처 파악
    ios_features_path = os.path.join(base_path, "iOS", "Features")
    if os.path.exists(ios_features_path):
        summary["features"] = [d for d in os.listdir(ios_features_path) if os.path.isdir(os.path.join(ios_features_path, d))]

    # 3. 주요 문서 내용 추출
    readme_path = os.path.join(base_path, "README.md")
    planning_path = os.path.join(base_path, "PaceSnap_Product_Planning_Document.md")
    
    readme_content = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
            readme_content = f.read()

    planning_content = ""
    if os.path.exists(planning_path):
        with open(planning_path, "r", encoding="utf-8", errors="ignore") as f:
            planning_content = f.read()

    # 4. 분석 결과 도출
    findings = []
    
    # README에서 명시된 제한사항 확인
    if "ActivitiesView" in readme_content and "RootView" in readme_content:
        findings.append("ActivitiesView(활동 지도·통계·공유 편집기)가 구현되어 있으나 RootView 메인 내비게이션에 미연결 상태")
    
    if "Tuist" in readme_content:
        findings.append("Tuist 4.x 기반 모듈형 Clean Architecture (Core / Domain / iOS Features)")

    if "HealthKit" in readme_content and "Photos" in readme_content:
        findings.append("HealthKit 운동 데이터 + Photos 사진 메타데이터 + MapKit 경로 오버레이 결합 앱")

    summary["key_findings"] = findings
    summary["readme_snippet"] = readme_content[:1000]
    return summary

if __name__ == "__main__":
    result = scan_project_structure()
    print("스캔 결과:", result["key_findings"])
    print("피처 목록:", result["features"])
    print("문서 목록:", result["documents"])
