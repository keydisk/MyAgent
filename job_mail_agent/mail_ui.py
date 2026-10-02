"""채용 메일 및 링크 요약 결과를 보여주는 macOS 스타일의 GUI 창 모듈.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess
from typing import List, Dict, Any

class JobMailWindow:
    def __init__(self, summarized_emails: List[Dict[str, Any]]):
        self.emails = summarized_emails
        self.current_index = 0
        
        self.root = tk.Tk()
        self.root.title("📬 macOS 채용 메일 알리미 & 요약")
        self.root.geometry("820x720")
        self.root.minsize(700, 600)
        
        # 다크/모던 테마 컬러
        self.bg_color = "#f8f9fa"
        self.card_bg = "#ffffff"
        self.primary_color = "#0066cc"
        self.text_main = "#1d1d1f"
        self.text_sub = "#6e6e73"
        self.border_color = "#e5e5ea"
        
        self.root.configure(bg=self.bg_color)
        
        # 스타일 구성
        self._setup_styles()
        self._build_ui()
        
        if self.emails:
            self.display_email(0)
            
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_bg, relief="solid", borderwidth=1)
        style.configure("TLabel", background=self.card_bg, foreground=self.text_main, font=("SF Pro Text", 12))
        style.configure("Header.TLabel", background=self.bg_color, foreground=self.text_main, font=("SF Pro Display", 18, "bold"))
        style.configure("SubHeader.TLabel", background=self.bg_color, foreground=self.text_sub, font=("SF Pro Text", 11))
        style.configure("Title.TLabel", background=self.card_bg, foreground=self.primary_color, font=("SF Pro Display", 14, "bold"))
        style.configure("Meta.TLabel", background=self.card_bg, foreground=self.text_sub, font=("SF Pro Text", 10))

    def _build_ui(self):
        # 헤더 영역
        header_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text=f"📬 채용 관련 수신 메일 ({len(self.emails)}건)",
            bg=self.bg_color,
            fg=self.text_main,
            font=("SF Pro Display", 18, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            header_frame,
            text="macOS Mail.app에서 수신된 채용 공고 및 링크 요약 정보입니다.",
            bg=self.bg_color,
            fg=self.text_sub,
            font=("SF Pro Text", 11)
        ).pack(anchor="w", pady=(2, 0))

        # 메일 선택 네비게이션 바
        nav_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=5)
        nav_frame.pack(fill="x")
        
        self.prev_btn = tk.Button(
            nav_frame, text="◀ 이전 메일", command=self.prev_mail,
            relief="flat", bg="#e5e5ea", fg=self.text_main, padx=10, pady=4, cursor="pointinghand"
        )
        self.prev_btn.pack(side="left")
        
        self.mail_counter_lbl = tk.Label(
            nav_frame, text="1 / 1", bg=self.bg_color, fg=self.text_main, font=("SF Pro Text", 11, "bold")
        )
        self.mail_counter_lbl.pack(side="left", padx=15)
        
        self.next_btn = tk.Button(
            nav_frame, text="다음 메일 ▶", command=self.next_mail,
            relief="flat", bg="#e5e5ea", fg=self.text_main, padx=10, pady=4, cursor="pointinghand"
        )
        self.next_btn.pack(side="left")

        open_mail_app_btn = tk.Button(
            nav_frame, text=" Mail 앱 열기", command=self.open_apple_mail,
            relief="flat", bg="#e3f2fd", fg="#0d47a1", padx=12, pady=4, cursor="pointinghand"
        )
        open_mail_app_btn.pack(side="right")

        # 본문 스크롤 영역
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)
        
        # 너비 리사이징 처리
        self.canvas.bind(
            '<Configure>',
            lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width)
        )
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 마우스 휠 스크롤 지원
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta)), "units")

    def open_apple_mail(self):
        subprocess.run(["open", "-a", "Mail"])

    def prev_mail(self):
        if self.current_index > 0:
            self.display_email(self.current_index - 1)

    def next_mail(self):
        if self.current_index < len(self.emails) - 1:
            self.display_email(self.current_index + 1)

    def display_email(self, index: int):
        self.current_index = index
        self.mail_counter_lbl.config(text=f"{index + 1} / {len(self.emails)}")
        self.prev_btn.config(state="normal" if index > 0 else "disabled")
        self.next_btn.config(state="normal" if index < len(self.emails) - 1 else "disabled")
        
        # 이전 컨텐츠 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        item = self.emails[index]

        # 1. 메일 기본 정보 카드
        card_info = tk.Frame(self.scrollable_frame, bg=self.card_bg, bd=1, relief="solid", padx=16, pady=14)
        card_info.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            card_info, text="✉️ " + item.get("subject", "제목 없음"),
            bg=self.card_bg, fg=self.primary_color, font=("SF Pro Display", 13, "bold"),
            wraplength=720, justify="left"
        ).pack(anchor="w")
        
        meta_text = f"발신자: {item.get('sender', '')}\n수신일: {item.get('date', '')}"
        tk.Label(
            card_info, text=meta_text,
            bg=self.card_bg, fg=self.text_sub, font=("SF Pro Text", 10),
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

        # 2. 채용 핵심 요약 카드
        card_summary = tk.Frame(self.scrollable_frame, bg=self.card_bg, bd=1, relief="solid", padx=16, pady=14)
        card_summary.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            card_summary, text="📌 채용 공고 핵심 요약",
            bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w")
        
        job_summary_lbl = tk.Label(
            card_summary, text=item.get("job_summary", ""),
            bg="#fdfefe", fg="#24292f", font=("SF Pro Text", 11),
            justify="left", wraplength=720, padx=8, pady=8, relief="groove", bd=1
        )
        job_summary_lbl.pack(fill="x", pady=(8, 0))

        # 3. 포함된 링크 및 웹페이지 요약 카드
        links = item.get("links", [])
        if links:
            card_links = tk.Frame(self.scrollable_frame, bg=self.card_bg, bd=1, relief="solid", padx=16, pady=14)
            card_links.pack(fill="x", pady=(0, 12))
            
            tk.Label(
                card_links, text=f"🔗 본문 내 주요 링크 및 웹 요약 ({len(links)}건)",
                bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
            ).pack(anchor="w")
            
            for i, link_info in enumerate(links, start=1):
                url = link_info.get("url", "")
                title = link_info.get("title", "")
                summary = link_info.get("summary", "")
                
                link_box = tk.Frame(card_links, bg="#f6f8fa", bd=1, relief="ridge", padx=10, pady=10)
                link_box.pack(fill="x", pady=(8, 4))
                
                # 링크 제목
                display_title = f"[{i}] {title}" if title else f"[{i}] 링크"
                tk.Label(
                    link_box, text=display_title,
                    bg="#f6f8fa", fg="#0969da", font=("SF Pro Text", 11, "bold"),
                    wraplength=680, justify="left"
                ).pack(anchor="w")
                
                # 웹 요약
                tk.Label(
                    link_box, text=summary,
                    bg="#f6f8fa", fg="#57606a", font=("SF Pro Text", 10),
                    wraplength=680, justify="left"
                ).pack(anchor="w", pady=(4, 6))
                
                # 열기 버튼과 URL 라벨
                action_row = tk.Frame(link_box, bg="#f6f8fa")
                action_row.pack(fill="x")
                
                url_display = url if len(url) <= 65 else url[:65] + "..."
                tk.Label(
                    action_row, text=url_display,
                    bg="#f6f8fa", fg="#8c959f", font=("Courier", 9)
                ).pack(side="left")
                
                open_btn = tk.Button(
                    action_row, text="🌐 페이지 열기",
                    command=lambda u=url: webbrowser.open(u),
                    bg="#0969da", fg="white", font=("SF Pro Text", 9, "bold"),
                    relief="flat", padx=8, pady=2, cursor="pointinghand"
                )
                open_btn.pack(side="right")
        else:
            card_no_links = tk.Frame(self.scrollable_frame, bg=self.card_bg, bd=1, relief="solid", padx=16, pady=10)
            card_no_links.pack(fill="x", pady=(0, 12))
            tk.Label(
                card_no_links, text="🔗 메일 본문에 감지된 외부 웹 링크가 없습니다.",
                bg=self.card_bg, fg=self.text_sub, font=("SF Pro Text", 11)
            ).pack(anchor="w")

        # 4. 메일 본문 원문 요약/텍스트
        card_content = tk.Frame(self.scrollable_frame, bg=self.card_bg, bd=1, relief="solid", padx=16, pady=14)
        card_content.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            card_content, text="📄 본문 텍스트 (미리보기)",
            bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w")
        
        text_box = tk.Text(
            card_content, height=8, wrap="word",
            bg="#fafbfc", fg="#24292f", font=("SF Pro Text", 10), relief="groove", bd=1
        )
        text_box.insert("1.0", item.get("raw_content", ""))
        text_box.config(state="disabled")
        text_box.pack(fill="x", pady=(8, 0))

        # 스크롤 최상단으로 리셋
        self.canvas.yview_moveto(0)

    def show(self):
        # 창을 화면 중앙에 배치
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # 포커스 활성화
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.mainloop()

def show_job_emails_ui(summarized_emails: List[Dict[str, Any]]):
    """UI 창 실행 헬퍼 함수"""
    if not summarized_emails:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "📬 채용 메일 확인 결과",
            "최근 수신함에 채용 관련 새로운 메일이 없습니다."
        )
        root.destroy()
        return

    win = JobMailWindow(summarized_emails)
    win.show()
