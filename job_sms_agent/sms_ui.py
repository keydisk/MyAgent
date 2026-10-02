"""구직/일 관련 수신 문자 요약 결과를 보여주는 macOS 스타일의 GUI 창 모듈.
"""

import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
from .sms_fetcher import open_privacy_settings

class SMSJobWindow:
    def __init__(self, summarized_sms_list: List[Dict[str, Any]], has_permission: bool = True, perm_msg: str = ""):
        self.sms_list = summarized_sms_list
        self.has_permission = has_permission
        self.perm_msg = perm_msg
        self.current_index = 0

        self.root = tk.Tk()
        self.root.title("💬 macOS 구직 & 업무 관련 문자 알리미")
        self.root.geometry("780x680")
        self.root.minsize(680, 560)

        self.bg_color = "#f8f9fa"
        self.card_bg = "#ffffff"
        self.primary_color = "#34c759"  # iMessage 그린
        self.accent_blue = "#007aff"
        self.text_main = "#1d1d1f"
        self.text_sub = "#6e6e73"

        self.root.configure(bg=self.bg_color)
        self._build_ui()

    def _build_ui(self):
        # 1. 상단 헤더
        header = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"💬 구직 및 업무 관련 수신 문자 ({len(self.sms_list)}건)",
            bg=self.bg_color, fg=self.text_main,
            font=("SF Pro Display", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="AI(Gemini 3.8 Flash High) 및 규칙 기반으로 분류된 문자 요약입니다.",
            bg=self.bg_color, fg=self.text_sub,
            font=("SF Pro Text", 11)
        ).pack(anchor="w", pady=(2, 0))

        # 권한 미허용 안내
        if not self.has_permission:
            perm_box = tk.Frame(self.root, bg="#fff3cd", padx=16, pady=14, relief="solid", bd=1)
            perm_box.pack(fill="x", padx=20, pady=(0, 10))

            tk.Label(
                perm_box,
                text="⚠️ macOS 보안 안내: 전체 디스크 접근 권한(Full Disk Access) 필요",
                bg="#fff3cd", fg="#856404",
                font=("SF Pro Text", 12, "bold")
            ).pack(anchor="w")

            tk.Label(
                perm_box,
                text=(
                    "macOS의 보안 정책으로 인해 메시지(chat.db)를 읽으려면\n"
                    "'시스템 설정 > 개인정보 보호 및 보안 > 전체 디스크 접근 권한'에서\n"
                    "터미널 또는 IDE(Cursor/Terminal/VSCode)의 스위치를 켜주셔야 합니다."
                ),
                bg="#fff3cd", fg="#664d03", justify="left",
                font=("SF Pro Text", 10)
            ).pack(anchor="w", pady=(4, 8))

            open_perm_btn = tk.Button(
                perm_box, text="⚙️ 시스템 설정(전체 디스크 접근 권한) 바로 열기",
                command=open_privacy_settings,
                bg="#856404", fg="white", font=("SF Pro Text", 10, "bold"),
                relief="flat", padx=12, pady=6, cursor="pointinghand"
            )
            open_perm_btn.pack(anchor="w")
            return

        # 2. 네비게이션 컨트롤 바
        nav_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=4)
        nav_frame.pack(fill="x")

        self.prev_btn = tk.Button(
            nav_frame, text="◀ 이전", command=self.prev_sms,
            relief="flat", bg="#e5e5ea", fg=self.text_main, padx=10, pady=4, cursor="pointinghand"
        )
        self.prev_btn.pack(side="left")

        self.counter_lbl = tk.Label(
            nav_frame, text="1 / 1", bg=self.bg_color, fg=self.text_main, font=("SF Pro Text", 11, "bold")
        )
        self.counter_lbl.pack(side="left", padx=15)

        self.next_btn = tk.Button(
            nav_frame, text="다음 ▶", command=self.next_sms,
            relief="flat", bg="#e5e5ea", fg=self.text_main, padx=10, pady=4, cursor="pointinghand"
        )
        self.next_btn.pack(side="left")

        open_msg_app_btn = tk.Button(
            nav_frame, text=" 메시지 앱 열기",
            command=lambda: subprocess.run(["open", "-a", "Messages"]),
            relief="flat", bg="#e8f5e9", fg="#2e7d32", padx=12, pady=4, cursor="pointinghand"
        )
        open_msg_app_btn.pack(side="right")

        # 3. 메인 스크롤 영역
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scroll_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind(
            '<Configure>',
            lambda event: self.canvas.itemconfig(self.canvas_win, width=event.width)
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.sms_list:
            self.display_sms(0)
        else:
            tk.Label(
                self.scroll_frame,
                text="최근 수신된 구직/업무 관련 문자가 없습니다.",
                bg=self.bg_color, fg=self.text_sub, font=("SF Pro Text", 12)
            ).pack(pady=40)

    def prev_sms(self):
        if self.current_index > 0:
            self.display_sms(self.current_index - 1)

    def next_sms(self):
        if self.current_index < len(self.sms_list) - 1:
            self.display_sms(self.current_index + 1)

    def display_sms(self, index: int):
        self.current_index = index
        self.counter_lbl.config(text=f"{index + 1} / {len(self.sms_list)}")
        self.prev_btn.config(state="normal" if index > 0 else "disabled")
        self.next_btn.config(state="normal" if index < len(self.sms_list) - 1 else "disabled")

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        item = self.sms_list[index]

        # 1. 발신자 & 메타 카드
        meta_card = tk.Frame(self.scroll_frame, bg=self.card_bg, padx=16, pady=12, relief="solid", bd=1)
        meta_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            meta_card, text=f"📱 발신처: {item.get('sender', '')}",
            bg=self.card_bg, fg=self.accent_blue, font=("SF Pro Display", 13, "bold")
        ).pack(anchor="w")

        meta_info = f"수신일시: {item.get('date', '')}  |  서비스: {item.get('service', 'SMS')}"
        tk.Label(
            meta_card, text=meta_info,
            bg=self.card_bg, fg=self.text_sub, font=("SF Pro Text", 10)
        ).pack(anchor="w", pady=(4, 0))

        # 2. AI & 핵심 요약 카드
        summary_card = tk.Frame(self.scroll_frame, bg=self.card_bg, padx=16, pady=14, relief="solid", bd=1)
        summary_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            summary_card, text="💡 구직/업무 핵심 요약 (Gemini 3.8 Flash High)",
            bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            summary_card, text=item.get("summary", ""),
            bg="#f0fdf4", fg="#166534", font=("SF Pro Text", 11),
            justify="left", wraplength=680, padx=10, pady=10, relief="groove", bd=1
        ).pack(fill="x", pady=(8, 0))

        # 3. 포함된 링크 카드
        links = item.get("links", [])
        if links:
            links_card = tk.Frame(self.scroll_frame, bg=self.card_bg, padx=16, pady=12, relief="solid", bd=1)
            links_card.pack(fill="x", pady=(0, 10))

            tk.Label(
                links_card, text=f"🔗 포함된 링크 요약 ({len(links)}건)",
                bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
            ).pack(anchor="w")

            for l in links:
                l_box = tk.Frame(links_card, bg="#f8fafc", padx=10, pady=8, relief="ridge", bd=1)
                l_box.pack(fill="x", pady=4)

                tk.Label(
                    l_box, text=l.get("title", "링크"),
                    bg="#f8fafc", fg="#0284c7", font=("SF Pro Text", 10, "bold"),
                    wraplength=640, justify="left"
                ).pack(anchor="w")

                tk.Label(
                    l_box, text=l.get("summary", ""),
                    bg="#f8fafc", fg="#475569", font=("SF Pro Text", 9),
                    wraplength=640, justify="left"
                ).pack(anchor="w", pady=(2, 4))

                u = l.get("url", "")
                btn = tk.Button(
                    l_box, text="🌐 링크 열기",
                    command=lambda target=u: webbrowser.open(target),
                    bg="#0284c7", fg="white", font=("SF Pro Text", 9),
                    relief="flat", padx=8, pady=2, cursor="pointinghand"
                )
                btn.pack(anchor="e")

        # 4. 문자 원문 텍스트
        raw_card = tk.Frame(self.scroll_frame, bg=self.card_bg, padx=16, pady=12, relief="solid", bd=1)
        raw_card.pack(fill="x", pady=(0, 20))

        tk.Label(
            raw_card, text="📜 문자 원문 내용",
            bg=self.card_bg, fg=self.text_main, font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w")

        txt = tk.Text(
            raw_card, height=6, wrap="word",
            bg="#fafbfc", fg="#334155", font=("SF Pro Text", 10),
            relief="groove", bd=1
        )
        txt.insert("1.0", item.get("raw_text", ""))
        txt.config(state="disabled")
        txt.pack(fill="x", pady=(6, 0))

    def show(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.mainloop()

def show_sms_ui(sms_list: List[Dict[str, Any]], has_permission: bool = True, perm_msg: str = ""):
    win = SMSJobWindow(sms_list, has_permission=has_permission, perm_msg=perm_msg)
    win.show()
