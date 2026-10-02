"""최주영 님의 커리어 자산 및 실행 가이드 연동 모듈.
'최주영_커리어_자산_및_실행_가이드.md'를 기반으로
채용 공고의 적합도(매칭도), 블랙리스트 배제 여부, 시니어 아키텍트 기준을 판정합니다.
"""

import os
import re
from typing import Dict, Any, List, Tuple

CAREER_DOC_PATH = "/Users/juyoungchoi/Documents/Project/MyAgent/최주영_커리어_자산_및_실행_가이드.md"

# 영구 제외 기업 (기재직사 11곳 + 이전 탈락/피로 기업 + 조건 미스매치 기업)
BLACKLIST_COMPANIES = [
    # 기재직사 11곳
    "SK인텔릭스", "아이지오", "하나투어", "암펠", "버넥트", "3i", "쓰리사이",
    "카카오VX", "카카오vx", "카페24", "쿠프마케팅", "피타소프트", "KG모빌리언스",
    "비티비솔루션", "한국공간정보통신",
    # 이전 지원 탈락 및 피로 기업
    "이든크루", "서울거래", "새하컴즈",
    # 저단가/조건 미스매치 배제 기업
    "중고나라", "트리플콤마", "위런에듀"
]

# 최주영 님 핵심 스킬 및 타깃 키워드
CORE_TARGET_KEYWORDS = [
    "모바일 아키텍트", "테크리드", "tech lead", "ios 리드", "flutter 리드",
    "시니어 ios", "시니어 flutter", "모바일 리드", "아키텍트", "architect",
    "swift", "swiftui", "flutter", "coreml", "metal", "vision", "healthkit"
]

# 배제 대상 키워드 (주니어/중급 한정 또는 미스매치 스택)
MISMATCH_KEYWORDS = [
    "신입", "인턴", "주니어", "1년 이상", "2년 이상", "3년 이상", "초급",
    "안드로이드 전용", "android only", "순수 백엔드", "java spring만",
    "퍼블리셔", "단순 웹 퍼블리싱"
]

def load_career_guide_text() -> str:
    """커리어 가이드 원문 로드"""
    if os.path.exists(CAREER_DOC_PATH):
        try:
            with open(CAREER_DOC_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[!] 커리어 가이드 읽기 오류: {e}")
    return ""

def get_career_summary_for_prompt() -> str:
    """Gemini 및 AI 프롬프트에 주입할 최주영 님의 핵심 커리어 프로필 요약"""
    return """[후보자: 최주영 엔지니어 핵심 커리어 프로필]
1. 연차 및 포지셔닝: 15~16년 차 모바일 아키텍트 / 테크리드 (만 42세)
2. 핵심 기술 스택:
   - iOS Native: Swift, SwiftUI, UIKit, Combine, Concurrency, Metal, CoreML, MapKit, HealthKit
   - Cross-platform: Flutter, Riverpod, Platform Channel (네이티브 브릿지)
   - AI/비전 엔지니어링: CoreML, MoveNet, YOLOv8, Metal GPU 셰이더, OpenCV, ARKit LiDAR
   - AI 워크플로우: Claude Code, Codex, MCP(Model Context Protocol) 1인 풀사이클
3. 핵심 대표 실적:
   - 카카오VX 골프예약 플랫폼: 초기 1인 출시 ~ 5년간 WAU 30만 규모 서비스 성장 및 아키텍처 리딩
   - 헬스케어/IoT: HealthKit, 라이다 포인트클라우드, Wi-Fi 블랙박스 통신
4. 지원 타깃 전략 (3-Tier):
   - Tier 1 (정규직): 15년 이상 오픈, 모바일 테크리드/아키텍트 포지션 (처우 협의)
   - Tier 2 (외주/프리): 월 800만원 이상 시니어 프로젝트 또는 주 1~2일 파트타임 테크리드 자문
   - Tier 3 (독립): 1인 마이크로 프로덕트(PaceSnap 등) 개발
5. 영구 제외(블랙리스트):
   - 기재직사: SK인텔릭스(아이지오), 하나투어(암펠), 버넥트, 3i, 카카오VX, 카페24, 쿠프마케팅, 피타소프트, KG모빌리언스, 비티비솔루션, 한국공간정보통신
   - 피로 기업: 이든크루, 서울거래, 새하컴즈, 중고나라, 트리플콤마, 위런에듀
   - 7년 이하 연차 상한 마감 공고 및 단순 저단가 SI는 전면 배제
"""

def evaluate_job_match(title: str, company: str, content: str) -> Dict[str, Any]:
    """
    공고 제목, 기업명, 본문 내용을 바탕으로 최주영 님과의 맞춤 적합도를 평가
    반환값:
      - grade: 'S' (테크리드/아키텍트 최적합), 'A' (추천 시니어), 'B' (검토 가능), 'F' (제외 대상)
      - badge: UI 표시용 배지 문자열
      - is_blacklisted: 블랙리스트 기업 여부
      - reason: 판정 사유
      - action_recommendation: 권장 액션
    """
    full_text = f"{title} {company} {content}".lower()

    # 1. 블랙리스트 기업 검사
    for black_company in BLACKLIST_COMPANIES:
        if black_company.lower() in full_text:
            return {
                "grade": "F",
                "badge": "🚫 제외 대상 (블랙리스트/기재직사)",
                "color": "#ef4444",
                "is_blacklisted": True,
                "reason": f"커리어 가이드에 명시된 영구 제외 기업({black_company})입니다.",
                "action_recommendation": "지원하지 않고 패스(Skip)합니다."
            }

    # 2. 미스매치/저연차 제한 검사
    is_junior_only = any(k in full_text for k in ["신입", "인턴", "주니어", "jr.", "jr ", "초급", "1~3년", "2~4년"])
    is_android_only = ("안드로이드" in full_text or "android" in full_text) and not ("ios" in full_text or "flutter" in full_text or "모바일" in full_text)

    if is_junior_only:
        return {
            "grade": "F",
            "badge": "⚠️ 저연차 제한 (주니어/초급 공고)",
            "color": "#f97316",
            "is_blacklisted": False,
            "reason": "주니어/초급 대상 포지션으로, 15년 차 시니어 아키텍트 지원 시 ATS 연차 상한 컷 또는 예산 미스매치 우려가 있습니다.",
            "action_recommendation": "소모전 방지를 위해 지원 패스(Skip) 권장."
        }

    if is_android_only:
        return {
            "grade": "F",
            "badge": "⚠️ 스택 미스매치 (Android 전용)",
            "color": "#6b7280",
            "is_blacklisted": False,
            "reason": "안드로이드 전용 공고로 최주영 님의 핵심 주특기(iOS/Flutter)와 불일치합니다.",
            "action_recommendation": "지원 제외 권장."
        }

    # 3. 최우수 매칭 (S등급: 테크리드 / 모바일 아키텍트 / 리드급 / 고단가)
    has_lead = any(k in full_text for k in ["리드", "lead", "아키텍트", "architect", "cto", "총괄", "파트장", "팀장", "10년", "15년"])
    has_target_stack = ("ios" in full_text or "swift" in full_text or "flutter" in full_text)

    if has_lead and has_target_stack:
        return {
            "grade": "S",
            "badge": "🔥 S등급: 최적합 (테크리드/아키텍트)",
            "color": "#10b981",
            "is_blacklisted": False,
            "reason": "최주영 님의 15년 차 시니어 모바일 아키텍트 및 테크리드 역량과 정확히 부합하는 포지션입니다.",
            "action_recommendation": "카카오VX WAU 30만 성장 리딩 및 AI 풀사이클 생산성을 강조하여 '처우 협의'로 적극 접수 권장!"
        }

    # 4. 우수 매칭 (A등급: 시니어 iOS / Flutter 개발자 / AI 비전)
    has_senior = any(k in full_text for k in ["시니어", "senior", "경력 5년 이상", "경력 7년 이상", "경력자", "상시채용"])
    has_ai_vision = any(k in full_text for k in ["vision", "ai", "coreml", "metal", "영상", "카메라", "헬스케어"])

    if has_target_stack:
        if has_ai_vision:
            return {
                "grade": "A+",
                "badge": "⚡ A+등급: 추천 (iOS/Flutter + AI/비전)",
                "color": "#0ea5e9",
                "is_blacklisted": False,
                "reason": "모바일과 온디바이스 AI/비전(MoveNet, CoreML, Metal) 특화 강점을 살릴 수 있는 포지션입니다.",
                "action_recommendation": "온디바이스 AI 프로덕트(PaceSnap 등) 포트폴리오를 첨부하여 지원 권장."
            }
        elif has_senior:
            return {
                "grade": "A",
                "badge": "✨ A등급: 추천 (시니어 모바일)",
                "color": "#3b82f6",
                "is_blacklisted": False,
                "reason": "시니어 iOS / Flutter 개발자 포지션으로 연차 및 기술 스택이 일치합니다.",
                "action_recommendation": "연차 상한을 확인하고 처우를 '협의'로 기재하여 가볍게 접수 고려."
            }
        else:
            return {
                "grade": "B",
                "badge": "📋 B등급: 일반 검토 가능",
                "color": "#f59e0b",
                "is_blacklisted": False,
                "reason": "모바일 개발 관련 공고이나 연차 상한(ATS) 또는 처우 적정성을 추가 확인해야 합니다.",
                "action_recommendation": "공고 상세 요건 확인 후 저연차 중심인지 필터링 필요."
            }

    # 5. 기타 일반 공고
    return {
        "grade": "C",
        "badge": "🔎 C등급: 단순 참고",
        "color": "#9ca3af",
        "is_blacklisted": False,
        "reason": "직접적인 모바일 아키텍트/테크리드 연관성이 낮거나 일반 IT 채용 정보입니다.",
        "action_recommendation": "단순 모니터링 수준으로 유지."
    }
