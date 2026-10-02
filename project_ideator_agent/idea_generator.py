"""PaceSnap(PhotoAndActivitiesApp) 프로젝트 개선 아이디어 생성 모듈.
최신 iOS 기술(iOS 18/17, Swift 6), 러닝 소셜 트렌드, HealthKit/MapKit 기술을 바탕으로
체계적이고 실현 가능한 개선안을 도출합니다.
"""

from datetime import datetime
from typing import Dict, Any, List
from .project_analyzer import scan_project_structure

def generate_daily_ideas(project_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """일일 개선 아이디어 리포트 데이터 생성"""
    if project_info is None:
        project_info = scan_project_structure()

    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    date_code = datetime.now().strftime("%Y%m%d")

    # 체계화된 아이디어 목록
    ideas = [
        {
            "id": 1,
            "badge": "UI/UX & 내비게이션",
            "title": "RootView 탭 바 개편 및 ActivitiesView 통합 연결",
            "priority": "🔥 높음 (High)",
            "difficulty": "중간",
            "summary": "현재 구현되었으나 진입점이 없는 ActivitiesView를 RootView의 메인 탭바에 연결하고 운동-사진 전환 플로우 완성",
            "problem": "README.md에 명시된 대로 ActivitiesView(운동 지도, 활동 관리, 차트와 공유 편집기)가 별도 구현되었으나 RootView 내비게이션에 연결되지 않아 사용자가 접근할 수 없음.",
            "solution": [
                "iOS/App/Sources/Presentation/RootView.swift에 3단 TabView(사진 라이브러리, 내 운동 활동 지도, 러닝 샷 에디터) 구현",
                "사진 상세 뷰(PhotoViewer)에서 해당 시점의 운동 기록으로 바로 점프하는 딥링크 내비게이션 추가",
                "운동 기록이 없는 사진과 운동 기록이 있는 사진을 구분하는 시각적 인디케이터(러닝화 아이콘 뱃지) 제공"
            ],
            "tech_stack": "SwiftUI, NavigationStack, AppCompositionRoot DI",
            "impact": "앱의 핵심 가치인 '운동과 사진의 결합' 경험이 메인 화면에서 온전히 활성화됨."
        },
        {
            "id": 2,
            "badge": "소셜 & 바이럴",
            "title": "인스타그램 스토리 규격(9:16) 다이내믹 러닝 인증샷 템플릿 엔진",
            "difficulty": "중간",
            "priority": "⚡ 추천 (Medium)",
            "summary": "러닝 크루와 인스타그래머를 위한 9:16 전용 세로형 감성 템플릿 및 고도/심박수/페이스 3D 루트 오버레이",
            "problem": "기존 러너들은 NRC나 스트라바의 제한적인 스티커 기능에 답답함을 느끼고 러닝 사진 위에 상세 페이스 차트와 경로를 예쁘게 올리고 싶어함.",
            "solution": [
                "인스타그램 스토리 맞춤형 9:16 종횡비 원클릭 템플릿 6종 (미니멀 화이트, 네온 다크, 사이버 트랙, 잡지 커버 에디션)",
                "사진 하단에 러닝 스플릿(1km당 페이스) 막대 그래프 및 심박존(Zone 1~5) 컬러 오버레이 렌더링",
                "지도 경로를 입체적인 반투명 3D 궤적으로 사진 위에 오버레이 합성하는 ImageRenderer 고도화"
            ],
            "tech_stack": "SwiftUI ImageRenderer, Metal Shader, CoreGraphics",
            "impact": "SNS 공유 바이럴 루프를 생성하여 신규 유저 유입 및 리텐션 대폭 향상."
        },
        {
            "id": 3,
            "badge": "외부 연동 & 생태계",
            "title": "Strava API 연동 및 GPX/FIT 트랙 파일 내보내기/가져오기",
            "difficulty": "중간",
            "priority": "⚡ 추천 (Medium)",
            "summary": "Garmin, Apple Watch, Strava 등 다른 기기나 앱에서 기록된 운동 데이터를 유연하게 가져오고 내보내는 기능",
            "problem": "HealthKit 외에 가민(Garmin) 워치 사용자가 많거나 타 러닝 앱 사용자의 데이터를 가져오는 유연성이 부족함.",
            "solution": [
                "Strava OAuth 2.0 연동을 통해 Strava 액티비티 동기화 및 PaceSnap 합성 사진 역업로드 지원",
                "표준 GPX 및 FIT 파서(Parser) 구현으로 외부 GPS 트랙 파일 드롭 & 사진 자동 시간 매칭",
                "사진의 EXIF 촬영 시간과 GPX 트랙 포인트를 타임스탬프 기준으로 정밀 보간(Interpolation)하여 위치 복원"
            ],
            "tech_stack": "URLSession, OAuth2, XMLParser/GPXKit, CoreLocation",
            "impact": "글로벌 러너 및 가민 사용자층까지 타겟 사용자층 대폭 확장."
        },
        {
            "id": 4,
            "badge": "AI & 컴퓨터 비전",
            "title": "On-Device Vision 기반 '베스트 러닝 샷' 자동 선별 및 피사체 세그멘테이션",
            "difficulty": "높음",
            "priority": "💡 신규 아이디어 (New)",
            "summary": "애플 Vision 프레임워크를 이용해 러닝 중 흔들리지 않은 인물 사진을 자동 추천하고, 인물 뒤로 러닝 경로 글자를 배치하는 감성 합성",
            "problem": "달리면서 찍은 사진 중 초점이 나갔거나 흔들린 사진이 많아 사용자가 좋은 사진을 고르는 데 피로감을 느낌.",
            "solution": [
                "Apple Vision Framework(VNRecognizeHumanBodyPoseRequest)로 역동적인 러닝 포즈 감지 및 점수화",
                "피사체(러너) 누끼 분리(Subject Lifting)를 적용하여 인물 뒷배경과 인물 사이에 페이스 텍스트(예: 05'23\") 배치",
                "얼굴 표정 및 눈 깜빡임 분석을 통한 '오늘의 인생 샷' 자동 1순위 추천 배지 부여"
            ],
            "tech_stack": "Vision.framework, CoreML, SwiftUI ShaderEffects (iOS 17+)",
            "impact": "경쟁 앱(NRC, Strava)에는 없는 독보적인 AI 사진 합성 UX로 확실한 차별화."
        },
        {
            "id": 5,
            "badge": "성능 & 아키텍처",
            "title": "Swift 6 Complete Concurrency 대응 및 Metal 지도 타일 렌더링 최적화",
            "difficulty": "낮음",
            "priority": "🛠 유지보수 (Maintenance)",
            "summary": "수만 개의 GPS 포인트와 고해상도 사진 썸네일 탐색 시 60fps 유지를 위한 메모리 및 렌더링 파이프라인 최적화",
            "problem": "장거리 마라톤(42.195km) 기록의 경우 수만 개의 좌표와 수백 장의 사진이 지도에 얹혀질 때 프레임 드랍 발생 가능.",
            "solution": [
                "R-Tree / Quadtree 기반 공간 인덱싱 알고리즘을 Core 모듈에 도입하여 화면 영역 밖 포인트 컬링",
                "Swift 6 Strict Concurrency 마이그레이션 및 Actor 격리를 통한 백그라운드 EXIF 파싱 병렬성 극대화",
                "Photos 프레임워크의 PHCachingImageManager 캐시 히트율 모니터링 및 메모리 경고 시 자동 비우기"
            ],
            "tech_stack": "Swift 6, Swift Concurrency (TaskGroup, Actor), Metal, Instruments",
            "impact": "배터리 소모량 25% 절감 및 장시간 지도 탐색 시 발열 억제."
        }
    ]

    report_data = {
        "report_id": f"PACESNAP-IDEA-{date_code}",
        "title": "PaceSnap (PhotoAndActivities) 데일리 프로젝트 혁신 리포트",
        "date_str": today_str,
        "date_code": date_code,
        "project_name": project_info.get("project_name", "PaceSnap"),
        "key_findings": project_info.get("key_findings", []),
        "features": project_info.get("features", []),
        "ideas": ideas,
        "author": "Antigravity AI Agent",
        "action_recommendation": "1순위로 'RootView 탭 바 개편 및 ActivitiesView 통합 연결' 작업을 시작하고, 이어 '인스타그램 9:16 템플릿 엔진' 브랜치를 생성하여 구현하는 것을 권장합니다."
    }
    return report_data
