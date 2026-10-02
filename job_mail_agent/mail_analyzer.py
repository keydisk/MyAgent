"""메일 본문 요약 및 메일 내 웹 링크 스크랩/요약 모듈
"""

import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional

class SimpleHTMLTextExtractor(HTMLParser):
    """HTML에서 텍스트와 타이틀/메타 설명을 추출하는 파서"""
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_desc = ""
        self.text_chunks = []
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()
        if tag_lower == 'title':
            self.in_title = True
        elif tag_lower in ['script', 'style', 'noscript']:
            self.in_script_or_style = True
        elif tag_lower == 'meta':
            name = attrs_dict.get('name', '').lower()
            prop = attrs_dict.get('property', '').lower()
            content = attrs_dict.get('content', '')
            if name in ['description', 'keywords'] or prop in ['og:description', 'og:title']:
                if not self.meta_desc and content:
                    self.meta_desc = content

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == 'title':
            self.in_title = False
        elif tag_lower in ['script', 'style', 'noscript']:
            self.in_script_or_style = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
        elif not self.in_script_or_style:
            cleaned = data.strip()
            if cleaned:
                self.text_chunks.append(cleaned)

    def get_summary_text(self, max_length: int = 500) -> str:
        full_text = " ".join(self.text_chunks)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        if len(full_text) > max_length:
            return full_text[:max_length] + "..."
        return full_text

def extract_urls(text: str, raw_source: str = "") -> List[str]:
    """텍스트 및 raw source(MIME)에서 실제 웹 URL을 정확하게 추출하고 필터링"""
    found_urls = []
    
    # 1. raw_source가 있으면 MIME 디코딩 수행
    if raw_source:
        try:
            import email
            from email import policy
            msg = email.message_from_string(raw_source, policy=policy.default)
            for part in msg.walk():
                ct = part.get_content_type()
                if ct in ['text/html', 'text/plain']:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded = payload.decode(charset, errors='replace')
                        found_urls.extend(re.findall(r'https?://[^\s<>"\'\)\;]+', decoded))
                        # href 속성 추출
                        found_urls.extend(re.findall(r'href=["\'](https?://[^"\']+)["\']', decoded, re.IGNORECASE))
        except Exception as e:
            print(f"[!] MIME 파싱 오류: {e}")

    # 2. 텍스트에서도 추출
    if text:
        found_urls.extend(re.findall(r'https?://[^\s<>"\'\)\;]+', text))

    # 3. URL 정제 및 리다이렉트 파라미터(url=...) 추출
    cleaned_urls = []
    for raw_u in found_urls:
        raw_u = raw_u.rstrip('.,;:)]>')
        # mcheck_utm.php?url=https%3A%2F%2F... 와 같은 추적 링크에서 실제 타겟 URL 파싱
        if "url=" in raw_u:
            try:
                parsed = urllib.parse.urlparse(raw_u)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'url' in qs and qs['url']:
                    target = urllib.parse.unquote(qs['url'][0])
                    if target.startswith("http"):
                        cleaned_urls.append(target)
            except Exception:
                pass
        cleaned_urls.append(raw_u)

    # 4. 필터링: 트래킹 픽셀, 구독 취소, 이미지 등 제외
    filtered = []
    seen = set()
    
    skip_keywords = [
        "unsubscribe", "reject", "optout", "privacy", "terms", "policy",
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".css", ".js",
        "doubleclick", "google-analytics", "pixel", "facebook.com/tr",
        "saraminimage", "mailinfo.saramin.co.kr/mail_ref", "static."
    ]
    
    for url in cleaned_urls:
        if url in seen:
            continue
        seen.add(url)
        
        lower_url = url.lower()
        if any(skip in lower_url for skip in skip_keywords):
            continue
            
        filtered.append(url)
        
    return filtered[:5] # 상위 5개 주요 링크 반환

def fetch_and_summarize_url(url: str, timeout: int = 5) -> Dict[str, str]:
    """URL의 웹페이지 내용을 가져와 제목 및 주요 내용을 요약"""
    result = {
        "url": url,
        "title": "",
        "summary": "링크 내용을 불러오지 못했습니다.",
        "success": False
    }
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # HTML content-type 확인
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                result["summary"] = f"HTML 페이지가 아님 ({content_type})"
                return result
                
            raw_data = response.read(150000) # 최대 150KB만 읽기
            encoding = response.headers.get_content_charset() or 'utf-8'
            try:
                html_text = raw_data.decode(encoding, errors='replace')
            except Exception:
                html_text = raw_data.decode('utf-8', errors='replace')
                
            parser = SimpleHTMLTextExtractor()
            parser.feed(html_text)
            
            title = parser.title.strip() or parser.meta_desc or "제목 없음"
            summary_content = parser.meta_desc or parser.get_summary_text(max_length=300)
            
            result["title"] = title
            result["summary"] = summary_content
            result["success"] = True
    except Exception as e:
        result["summary"] = f"접속 오류 ({type(e).__name__}): {str(e)[:60]}"
        
    return result

def summarize_job_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    채용 관련 메일의 텍스트 본문과 링크를 분석하여
    핵심 채용 정보 요약 및 링크 요약 결과를 딕셔너리로 반환
    """
    subject = email_data.get("subject", "")
    sender = email_data.get("sender", "")
    date_str = email_data.get("date", "")
    content = email_data.get("content", "")
    source = email_data.get("source", "")
    
    # 1. 최주영 님 커리어 가이드 기반 적합도 판정
    from common.career_profile import evaluate_job_match, get_career_summary_for_prompt
    fit_eval = evaluate_job_match(title=subject, company=sender, content=content)

    # 2. Gemini 3.8 Flash High 요약 시도 (커리어 가이드 컨텍스트 주입)
    from common.gemini_client import call_gemini
    gemini_prompt = (
        f"{get_career_summary_for_prompt()}\n\n"
        f"위 후보자(최주영 님)의 커리어 전략과 백그라운드를 기준으로 다음 채용 메일을 분석해주세요.\n"
        f"- 메일 제목: {subject}\n"
        f"- 발신자: {sender}\n"
        f"- 본문:\n{content[:2500]}\n\n"
        f"작성 규칙:\n"
        f"1. 최주영 님에게 적합한 시니어 모바일/테크리드/Flutter/AI 관점에서 핵심 공고와 조건을 3줄로 요약\n"
        f"2. 연차 상한(ATS) 주의점이나 추천/패스 사유를 한 줄 덧붙여주세요."
    )
    ai_summary = call_gemini(gemini_prompt, system_instruction="당신은 15년차 모바일 아키텍트 최주영 님의 전담 수석 커리어 에이전트입니다.")

    if ai_summary:
        pos_summary = ai_summary
    else:
        # 본문 텍스트 정리 및 구조화 (휴리스틱 요약기)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        positions = []
        key_lines = []
        
        for line in lines:
            if any(k in line for k in ["개발", "엔지니어", "모집", "채용", "기획", "디자이너", "경력", "신입", "정규직", "원격"]):
                if len(line) < 100:
                    positions.append(line)
            if len(key_lines) < 8 and len(line) > 10 and not line.startswith("http"):
                key_lines.append(line)

        if positions:
            pos_summary = "\n".join([f"• {p}" for p in positions[:8]])
            if len(positions) > 8:
                pos_summary += f"\n... 외 {len(positions) - 8}개 항목"
        else:
            pos_summary = "\n".join([f"• {l}" for l in key_lines[:5]]) or "본문에서 추출된 채용 요약이 없습니다."

    # 3. URL 추출 및 링크 요약
    urls = extract_urls(content, source)
    link_summaries = []
    
    print(f"[*] '{subject[:25]}...' 메일에서 {len(urls)}개의 링크를 분석합니다...")
    for u in urls[:3]: # 주요 링크 최대 3개 분석
        res = fetch_and_summarize_url(u)
        link_summaries.append(res)
        
    return {
        "subject": subject,
        "sender": sender,
        "date": date_str,
        "job_summary": pos_summary,
        "links": link_summaries,
        "fit_eval": fit_eval,
        "raw_content": content[:1500]
    }
