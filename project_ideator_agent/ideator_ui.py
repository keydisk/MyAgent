"""생성된 PDF를 띄우고, 사용자로부터 에이전트 지시사항을 입력받는 인터랙티브 제어 UI 모듈.
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any

INSTRUCTIONS_LOG_FILE = "/Users/juyoungchoi/Documents/Project/MyAgent/instructions_log.json"
PENDING_TASK_FILE = "/Users/juyoungchoi/Documents/Project/MyAgent/PENDING_INSTRUCTION.md"

class ProjectIdeatorWindow:
    def __init__(self, pdf_path: str, report_data: Dict[str, Any]):
        self.pdf_path = pdf_path
        self.report_data = report_data
        
        self.root = tk.Tk()
        self.root.title("🏃‍♂️ PaceSnap 프로젝트 혁신 리포트 & 에이전트 지시 콘솔")
        self.root.geometry("860x780")
        self.root.minsize(760, 680)
        
        self.bg_color = "#f8f9fa"
        self.card_bg = "#ffffff"
        self.primary_color = "#0066cc"
        self.success_color = "#10b981"
        self.text_main = "#1d1d1f"
        self.text_sub = "#6e6e73"
        self.border_color = "#e5e5ea"
        
        self.root.configure(bg=self.bg_color)
        self._build_ui()
        
        # PDF 자동으로 기본 뷰어로 열기
        self.open_pdf()

    def open_pdf(self):
        """macOS 기본 PDF 뷰어(미리보기)로 PDF 파일 열기"""
        if os.path.exists(self.pdf_path):
            subprocess.run(["open", self.pdf_path])
        else:
            messagebox.showerror("오류", f"PDF 파일을 찾을 수 없습니다: {self.pdf_path}")

    def _build_ui(self):
        # 1. 헤더 영역
        header = tk.Frame(self.root, bg=self.bg_color, padx=24, pady=16)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="🚀 PaceSnap 일일 개선 아이디어 리포트",
            bg=self.bg_color, fg=self.text_main,
            font=("SF Pro Display", 18, "bold")
        ).pack(anchor="w")
        
        date_str = self.report_data.get("date_str", "")
        tk.Label(
            header,
            text=f"일자: {date_str} • 대상: /Users/juyoungchoi/Documents/Project/PhotoAndActivitiesApp",
            bg=self.bg_color, fg=self.text_sub,
            font=("SF Pro Text", 11)
        ).pack(anchor="w", pady=(2, 0))

        # 2. PDF 안내 및 컨트롤 바
        pdf_bar = tk.Frame(self.root, bg="#eef2ff", padx=20, pady=12, relief="solid", bd=1)
        pdf_bar.pack(fill="x", padx=24, pady=(0, 12))
        
        pdf_info_col = tk.Frame(pdf_bar, bg="#eef2ff")
        pdf_info_col.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            pdf_info_col,
            text="📄 고화질 아이디어 PDF 리포트가 생성되었습니다.",
            bg="#eef2ff", fg="#1e40af",
            font=("SF Pro Text", 11, "bold")
        ).pack(anchor="w")
        
        file_basename = os.path.basename(self.pdf_path)
        tk.Label(
            pdf_info_col,
            text=f"저장 위치: {file_basename}",
            bg="#eef2ff", fg="#475569",
            font=("Courier", 10)
        ).pack(anchor="w", pady=(2, 0))
        
        open_pdf_btn = tk.Button(
            pdf_bar, text="🔍 PDF 다시 열기",
            command=self.open_pdf,
            bg=self.primary_color, fg="white",
            font=("SF Pro Text", 11, "bold"),
            relief="flat", padx=14, pady=6, cursor="pointinghand"
        )
        open_pdf_btn.pack(side="right")

        # 3. 중앙 분할 영역 (아이디어 퀵 선택 + 지시 입력)
        main_body = tk.Frame(self.root, bg=self.bg_color, padx=24)
        main_body.pack(fill="both", expand=True)

        # 3-1. 아이디어 목록 퀵 선택 카드
        quick_card = tk.Frame(main_body, bg=self.card_bg, padx=16, pady=14, relief="solid", bd=1)
        quick_card.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            quick_card,
            text="💡 오늘 제안된 5대 핵심 아이디어 (클릭 시 지시창에 자동 입력)",
            bg=self.card_bg, fg=self.text_main,
            font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        ideas = self.report_data.get("ideas", [])
        for idea in ideas:
            btn_text = f"#{idea['id']} [{idea['badge']}] {idea['title']}"
            btn = tk.Button(
                quick_card, text=btn_text,
                anchor="w", justify="left",
                command=lambda i=idea: self.select_idea(i),
                bg="#f1f5f9", fg="#0f172a",
                font=("SF Pro Text", 10),
                relief="flat", padx=10, pady=5, cursor="pointinghand"
            )
            btn.pack(fill="x", pady=2)

        # 3-2. 에이전트 지시 입력창 카드
        instruct_card = tk.Frame(main_body, bg=self.card_bg, padx=16, pady=14, relief="solid", bd=1)
        instruct_card.pack(fill="both", expand=True, pady=(0, 12))
        
        tk.Label(
            instruct_card,
            text="✍️ 에이전트(Antigravity)에게 지시할 작업 내용 입력",
            bg=self.card_bg, fg=self.primary_color,
            font=("SF Pro Text", 12, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            instruct_card,
            text="위 아이디어 중 하나를 선택하거나, 새로운 기능 추가·리팩토링·GitHub 커밋 지시를 자유롭게 작성하세요.",
            bg=self.card_bg, fg=self.text_sub,
            font=("SF Pro Text", 10)
        ).pack(anchor="w", pady=(2, 6))

        self.instruction_text = tk.Text(
            instruct_card, height=6, wrap="word",
            bg="#fafbfc", fg="#1f2937",
            font=("SF Pro Text", 11),
            relief="solid", bd=1, padx=8, pady=8
        )
        self.instruction_text.pack(fill="both", expand=True)
        default_prompt = (
            "아이디어 #1번 'RootView 탭 바 개편 및 ActivitiesView 통합 연결' 작업을 시작해줘.\n"
            "- 필요한 SwiftUI 파일 변경사항을 작성해줘.\n"
            "- 완료되면 내 GitHub에 새 브랜치를 만들어 커밋하고 푸시해줘."
        )
        self.instruction_text.insert("1.0", default_prompt)

        # 4. 하단 액션 버튼 바
        action_bar = tk.Frame(self.root, bg=self.bg_color, padx=24, pady=12)
        action_bar.pack(fill="x")
        
        github_sync_btn = tk.Button(
            action_bar, text="🐙 GitHub 저장소 동기화 / 푸시",
            command=self.sync_github,
            bg="#24292f", fg="white",
            font=("SF Pro Text", 11),
            relief="flat", padx=14, pady=8, cursor="pointinghand"
        )
        github_sync_btn.pack(side="left")

        submit_btn = tk.Button(
            action_bar, text="🚀 지시 전달 및 작업 접수",
            command=self.submit_instruction,
            bg=self.success_color, fg="white",
            font=("SF Pro Text", 11, "bold"),
            relief="flat", padx=20, pady=8, cursor="pointinghand"
        )
        submit_btn.pack(side="right")

    def select_idea(self, idea: Dict[str, Any]):
        prompt = (
            f"아이디어 #{idea['id']}번 '{idea['title']}' 구현을 지시합니다.\n\n"
            f"- 핵심 목표: {idea['summary']}\n"
            f"- 기술 스택: {idea['tech_stack']}\n"
            f"- 요구사항:\n"
        )
        for s in idea.get("solution", []):
            prompt += f"  • {s}\n"
        prompt += "\n작업 완료 후 GitHub에 커밋 및 푸시해줘."
        
        self.instruction_text.delete("1.0", "end")
        self.instruction_text.insert("1.0", prompt)

    def submit_instruction(self):
        user_input = self.instruction_text.get("1.0", "end").strip()
        if not user_input:
            messagebox.showwarning("입력 필요", "에이전트에게 전달할 지시 내용을 입력해주세요.")
            return

        now_str = datetime.now().isoformat()
        instruction_payload = {
            "timestamp": now_str,
            "pdf_path": self.pdf_path,
            "instruction": user_input,
            "status": "QUEUED"
        }

        # 1. instructions_log.json에 누적 저장
        logs = []
        if os.path.exists(INSTRUCTIONS_LOG_FILE):
            try:
                with open(INSTRUCTIONS_LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(instruction_payload)
        with open(INSTRUCTIONS_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        # 2. PENDING_INSTRUCTION.md 작성 (에이전트 실시간 감지용)
        pending_md = f"""# 📋 에이전트 작업 지시서 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

## 📌 참조 PDF 리포트
- `{self.pdf_path}`

## ✍️ 사용자 지시 사항
```
{user_input}
```

## 🔄 상태
- `접수 완료 (PENDING)`
"""
        with open(PENDING_TASK_FILE, "w", encoding="utf-8") as f:
            f.write(pending_md)

        messagebox.showinfo(
            "✅ 지시 접수 완료",
            "사용자님의 지시사항이 에이전트(Antigravity)에 성공적으로 접수되었습니다!\n\n"
            "지시서가 PENDING_INSTRUCTION.md에 기록되었으며\n"
            "채팅창 또는 백그라운드 태스크에서 즉시 작업이 수행됩니다."
        )
        self.root.destroy()

    def sync_github(self):
        """GitHub 동기화 CLI 호출"""
        try:
            from github_manager.git_service import sync_and_push_repo
            success, msg = sync_and_push_repo()
            if success:
                messagebox.showinfo("GitHub 동기화 성공", f"GitHub에 성공적으로 반영되었습니다:\n{msg}")
            else:
                messagebox.showerror("GitHub 동기화 오류", f"동기화 중 오류 발생:\n{msg}")
        except Exception as e:
            messagebox.showerror("오류", f"GitHub 모듈 실행 실패: {e}")

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

def show_ideator_window(pdf_path: str, report_data: Dict[str, Any]):
    win = ProjectIdeatorWindow(pdf_path, report_data)
    win.show()
