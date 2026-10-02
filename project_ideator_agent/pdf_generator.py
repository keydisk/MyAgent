"""아이디어 리포트를 시각적으로 미려한 HTML로 빌드한 후
Google Chrome Headless 엔진을 통해 프리미엄 PDF 문서로 생성하는 모듈.
"""

import os
import subprocess
from typing import Dict, Any

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def generate_report_html(report_data: Dict[str, Any]) -> str:
    """HTML 템플릿 렌더링"""
    title = report_data.get("title", "PaceSnap 개선 아이디어 리포트")
    date_str = report_data.get("date_str", "")
    report_id = report_data.get("report_id", "")
    key_findings = report_data.get("key_findings", [])
    ideas = report_data.get("ideas", [])
    recommendation = report_data.get("action_recommendation", "")

    # Findings HTML
    findings_html = "".join([f"<li>{f}</li>" for f in key_findings])

    # Ideas HTML
    ideas_html_list = []
    for idea in ideas:
        sol_items = "".join([f"<li>{s}</li>" for s in idea.get("solution", [])])
        priority_color = "#e53e3e" if "높음" in idea.get("priority", "") else "#2b6cb0"
        
        card = f"""
        <div class="idea-card">
            <div class="idea-header">
                <div class="idea-badge">{idea.get('badge', '')}</div>
                <div class="idea-priority" style="color: {priority_color};">{idea.get('priority', '')} (난이도: {idea.get('difficulty', '')})</div>
            </div>
            <h2 class="idea-title">#{idea.get('id')} {idea.get('title')}</h2>
            <p class="idea-summary"><strong>요약:</strong> {idea.get('summary')}</p>
            
            <div class="section-box">
                <div class="box-label">🔍 문제 정의 & 배경</div>
                <p>{idea.get('problem')}</p>
            </div>
            
            <div class="section-box">
                <div class="box-label">💡 구체적 구현 방안</div>
                <ul>{sol_items}</ul>
            </div>
            
            <div class="meta-row">
                <span class="meta-item">🛠 <strong>기술 스택:</strong> {idea.get('tech_stack')}</span>
                <span class="meta-item">📈 <strong>기대 효과:</strong> {idea.get('impact')}</span>
            </div>
        </div>
        """
        ideas_html_list.append(card)

    ideas_combined = "\n".join(ideas_html_list)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm;
        }}
        html {{
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            font-size: 13px;
            color: #1f2937;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #ffffff;
        }}
        .header {{
            border-bottom: 3px solid #0066cc;
            padding-bottom: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .header-title-box h1 {{
            font-size: 24px;
            color: #0f172a;
            margin: 0 0 6px 0;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .header-title-box .subtitle {{
            font-size: 13px;
            color: #64748b;
            margin: 0;
        }}
        .header-meta {{
            text-align: right;
            font-size: 11px;
            color: #475569;
        }}
        .overview-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #0066cc;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 24px;
        }}
        .overview-box h3 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #0f172a;
        }}
        .overview-box ul {{
            margin: 0;
            padding-left: 18px;
            color: #334155;
        }}
        .idea-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            page-break-inside: avoid;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .idea-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .idea-badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0284c7;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .idea-priority {{
            font-size: 11px;
            font-weight: 700;
        }}
        .idea-title {{
            font-size: 17px;
            color: #0f172a;
            margin: 0 0 8px 0;
            font-weight: 700;
        }}
        .idea-summary {{
            margin: 0 0 12px 0;
            font-size: 13px;
            color: #334155;
        }}
        .section-box {{
            background: #f8fafc;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }}
        .box-label {{
            font-size: 11px;
            font-weight: 700;
            color: #475569;
            margin-bottom: 4px;
            text-transform: uppercase;
        }}
        .section-box p {{
            margin: 0;
            font-size: 12px;
            color: #334155;
        }}
        .section-box ul {{
            margin: 0;
            padding-left: 16px;
            font-size: 12px;
            color: #334155;
        }}
        .section-box li {{
            margin-bottom: 3px;
        }}
        .meta-row {{
            margin-top: 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            font-size: 11px;
            background: #f1f5f9;
            padding: 8px 12px;
            border-radius: 6px;
        }}
        .recommendation-box {{
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            border-left: 4px solid #10b981;
            padding: 14px 18px;
            border-radius: 6px;
            margin-top: 24px;
            page-break-inside: avoid;
        }}
        .recommendation-box h3 {{
            margin: 0 0 6px 0;
            color: #065f46;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 28px;
            text-align: center;
            font-size: 11px;
            color: #94a3b8;
            border-top: 1px solid #f1f5f9;
            padding-top: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title-box">
            <h1>🏃‍♂️ {title}</h1>
            <p class="subtitle">대상 프로젝트: <code>{report_data.get('project_name')}</code> (/Users/juyoungchoi/Documents/Project/PhotoAndActivitiesApp)</p>
        </div>
        <div class="header-meta">
            <div><strong>일자:</strong> {date_str}</div>
            <div><strong>문서 ID:</strong> {report_id}</div>
            <div><strong>작성:</strong> Antigravity AI Agent</div>
        </div>
    </div>

    <div class="overview-box">
        <h3>📌 프로젝트 현황 분석 및 중점 개선 포인트</h3>
        <ul>
            {findings_html}
        </ul>
    </div>

    {ideas_combined}

    <div class="recommendation-box">
        <h3>🚀 종합 추진 로드맵 및 액션 제안</h3>
        <p style="margin: 0; font-size: 13px; color: #047857;">{recommendation}</p>
    </div>

    <div class="footer">
        Generated automatically by MyAgent Project Ideator • 평일 오전 11시 일일 자동 생성 리포트
    </div>
</body>
</html>
"""
    return html

def build_pdf_report(report_data: Dict[str, Any], output_dir: str = "/Users/juyoungchoi/Documents/Project/MyAgent/output") -> str:
    """HTML 생성 후 Chrome Headless를 사용해 PDF 파일로 렌더링"""
    os.makedirs(output_dir, exist_ok=True)
    date_code = report_data.get("date_code", "daily")
    output_pdf_path = os.path.join(output_dir, f"PaceSnap_Improvement_Ideas_{date_code}.pdf")
    temp_html_path = os.path.join(output_dir, f"temp_report_{date_code}.html")

    html_content = generate_report_html(report_data)
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[*] HTML 리포트 저장 완료: {temp_html_path}")
    print(f"[*] Google Chrome Headless 엔진으로 PDF 변환 중: {output_pdf_path}...")

    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        temp_html_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[✓] PDF 생성 성공: {output_pdf_path}")
    except Exception as e:
        print(f"[!] Chrome PDF 렌더링 실패: {e}")
        return temp_html_path
    finally:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

    return output_pdf_path
