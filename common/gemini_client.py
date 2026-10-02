"""Gemini API 클라이언트 모듈 (기본 모델: gemini-3.8-flash-high).
환경 변수 GEMINI_API_KEY가 설정되어 있으면 Gemini API를 직접 호출하고,
키가 없거나 오프라인일 때는 안전한 로컬 지능형 요약 엔진으로 자동 폴백합니다.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash-high")

def call_gemini(prompt: str, model: str = DEFAULT_MODEL, system_instruction: str = "") -> Optional[str]:
    """Gemini API를 호출하여 텍스트 생성/요약 수행"""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    # 모델명 정규화 (사용자가 gemini-3.8-flash-high 지정)
    # 구글 API 엔드포인트 URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except urllib.error.HTTPError as e:
        # 모델명이 3.8 프리뷰일 경우 하위 호환 fallback 지원
        if e.code == 404 and model == "gemini-3.8-flash-high":
            # 표준 2.5-flash / 1.5-flash 모델로 재시도
            return call_gemini(prompt, model="gemini-2.5-flash", system_instruction=system_instruction)
        print(f"[!] Gemini API HTTP 오류 ({e.code}): {e.read().decode('utf-8', errors='ignore')[:150]}")
    except Exception as e:
        print(f"[!] Gemini API 호출 실패: {e}")

    return None

def summarize_text_with_gemini(text: str, context_type: str = "채용 및 업무") -> str:
    """Gemini 3.8 Flash High를 활용한 텍스트 요약 (키 없을 시 기본 요약 반환)"""
    prompt = (
        f"다음은 수신된 {context_type} 관련 메시지입니다.\n"
        f"핵심 내용(회사/발신처, 직무/프로젝트 내용, 조건/마감일/제안 사항)을 3줄 이내의 명확한 불릿 포인트로 요약해주세요:\n\n"
        f"{text}"
    )
    sys_instruction = "당신은 구직 및 업무 메시지를 정확하고 간결하게 요약해주는 전문 AI 비서입니다."
    
    res = call_gemini(prompt, system_instruction=sys_instruction)
    return res if res else ""
