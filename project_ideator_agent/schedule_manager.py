"""macOS launchd를 이용한 평일 오전 11시 스케줄링 관리 모듈.
"""

import os
import subprocess
from typing import Tuple

PLIST_LABEL = "com.myagent.ideator"
PLIST_FILENAME = f"{PLIST_LABEL}.plist"
LAUNCH_AGENTS_DIR = os.path.expanduser("~/Library/LaunchAgents")
PLIST_PATH = os.path.join(LAUNCH_AGENTS_DIR, PLIST_FILENAME)

MAIN_PY_PATH = "/Users/juyoungchoi/Documents/Project/MyAgent/main.py"
PYTHON_BIN = "/usr/bin/python3"
LOG_OUT = "/Users/juyoungchoi/Documents/Project/MyAgent/output/launchd_ideator.log"
LOG_ERR = "/Users/juyoungchoi/Documents/Project/MyAgent/output/launchd_ideator.err"

PLIST_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON_BIN}</string>
        <string>{MAIN_PY_PATH}</string>
        <string>ideate</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <!-- 월요일 11:00 AM -->
        <dict>
            <key>Weekday</key>
            <integer>1</integer>
            <key>Hour</key>
            <integer>11</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- 화요일 11:00 AM -->
        <dict>
            <key>Weekday</key>
            <integer>2</integer>
            <key>Hour</key>
            <integer>11</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- 수요일 11:00 AM -->
        <dict>
            <key>Weekday</key>
            <integer>3</integer>
            <key>Hour</key>
            <integer>11</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- 목요일 11:00 AM -->
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>11</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- 금요일 11:00 AM -->
        <dict>
            <key>Weekday</key>
            <integer>5</integer>
            <key>Hour</key>
            <integer>11</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardOutPath</key>
    <string>{LOG_OUT}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_ERR}</string>
</dict>
</plist>
"""

def install_launchd_schedule() -> Tuple[bool, str]:
    """launchd plist 파일을 생성하고 launchctl에 로드하여 평일 오전 11시 스케줄 활성화"""
    try:
        os.makedirs(LAUNCH_AGENTS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(LOG_OUT), exist_ok=True)

        # 기존 서비스가 있다면 언로드
        if os.path.exists(PLIST_PATH):
            subprocess.run(["launchctl", "unload", PLIST_PATH], stderr=subprocess.DEVNULL)

        # plist 파일 작성
        with open(PLIST_PATH, "w", encoding="utf-8") as f:
            f.write(PLIST_CONTENT)

        # launchctl에 등록
        res = subprocess.run(["launchctl", "load", PLIST_PATH], capture_output=True, text=True)
        if res.returncode == 0:
            return True, f"성공적으로 등록되었습니다!\n- Plist 경로: {PLIST_PATH}\n- 실행 주기: 평일(월~금) 오전 11:00"
        else:
            return False, f"launchctl load 실패: {res.stderr}"
    except Exception as e:
        return False, f"오류 발생: {str(e)}"

def uninstall_launchd_schedule() -> Tuple[bool, str]:
    """launchd 스케줄 해제 및 plist 파일 삭제"""
    try:
        if os.path.exists(PLIST_PATH):
            subprocess.run(["launchctl", "unload", PLIST_PATH], stderr=subprocess.DEVNULL)
            os.remove(PLIST_PATH)
            return True, "스케줄이 성공적으로 해제되었습니다."
        else:
            return True, "등록된 스케줄이 없습니다."
    except Exception as e:
        return False, f"오류 발생: {str(e)}"

def check_schedule_status() -> str:
    """현재 스케줄 등록 상태 점검"""
    is_installed = os.path.exists(PLIST_PATH)
    if not is_installed:
        return "❌ 스케줄 미등록 상태 (설치하려면 python3 main.py schedule-ideator 실행)"

    # launchctl list에서 확인
    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    in_launchctl = PLIST_LABEL in res.stdout
    
    status_str = f"✅ 스케줄 등록 완료!\n"
    status_str += f"- Plist: {PLIST_PATH}\n"
    status_str += f"- launchctl 상태: {'실행 대기 중 (Active)' if in_launchctl else '로드 대기'}\n"
    status_str += f"- 스케줄: 매주 월~금(평일) 오전 11:00 정각\n"
    status_str += f"- 로그: {LOG_OUT}"
    return status_str

if __name__ == "__main__":
    success, msg = install_launchd_schedule()
    print(msg)
    print("\n[현재 상태]")
    print(check_schedule_status())
