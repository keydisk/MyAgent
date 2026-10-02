"""ReportLab과 macOS 한글 TTF를 사용한 PDF 생성기."""

import json
import sys
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def build(report, output, day):
    font = Path('/System/Library/Fonts/Supplemental/AppleGothic.ttf')
    if not font.is_file():
        raise RuntimeError('한글 폰트 AppleGothic.ttf를 찾을 수 없습니다.')
    pdfmetrics.registerFont(TTFont('Korean', str(font)))
    body = ParagraphStyle('Body', fontName='Korean', fontSize=10, leading=16,
                          spaceAfter=7, wordWrap='CJK', alignment=TA_LEFT)
    title = ParagraphStyle('Title', parent=body, fontSize=23, leading=30,
                           textColor=colors.HexColor('#155e75'), spaceAfter=14)
    heading = ParagraphStyle('Heading', parent=body, fontSize=14, leading=22,
                             spaceBefore=14, keepWithNext=True)
    story = [Paragraph('PaceSnap 수익화 조사', title),
             Paragraph(f'{day} · 한국 시간 · gpt-6-luna / medium', body),
             Paragraph(escape(report['summary']), heading),
             Paragraph(escape(report['next_action']), body)]
    for section in report['sections']:
        story.append(Paragraph(escape(section['heading']), heading))
        for line in section['body'].splitlines():
            if line.strip():
                story.append(Paragraph(escape(line), body))
            else:
                story.append(Spacer(1, 4))
    story.append(Paragraph(f'출처 (확인일: {day})', heading))
    for index, source in enumerate(report['sources'], 1):
        url = escape(source['url'], quote=True)
        story.append(Paragraph(f'[{index}] {escape(source["title"])}<br/>'
                               f'<link href="{url}" color="#155e75">{url}</link>', body))
    story.append(Paragraph('영업일 확인', heading))
    story.append(Paragraph(escape(report['calendar_reason']), body))
    url = escape(report['calendar_source'], quote=True)
    story.append(Paragraph(f'<link href="{url}" color="#155e75">{url}</link>', body))

    def footer(canvas, document):
        canvas.setFont('Korean', 9)
        canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(document.page))

    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                      topMargin=18 * mm, bottomMargin=18 * mm,
                      title=f'PaceSnap 수익화 조사 {day}', author='MyAgent').build(
                          story, onFirstPage=footer, onLaterPages=footer)


if __name__ == '__main__':
    build(json.load(sys.stdin), Path(sys.argv[1]), sys.argv[2])
