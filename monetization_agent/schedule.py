"""main.py monetization을 평일 11시에 실행하는 macOS LaunchAgent."""

import os
import plistlib
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .run import ROOT, OUTPUT, SEOUL

LABEL = 'com.myagent.monetization'
PLIST = Path.home() / 'Library' / 'LaunchAgents' / f'{LABEL}.plist'


def schedule_config():
    return {
        'Label': LABEL,
        'ProgramArguments': [sys.executable, str(ROOT / 'main.py'), 'monetization'],
        'WorkingDirectory': str(ROOT),
        'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
                                 'TZ': 'Asia/Seoul', 'PYTHONUNBUFFERED': '1'},
        'StartCalendarInterval': [{'Weekday': day, 'Hour': 11, 'Minute': 0} for day in range(1, 6)],
        'StandardOutPath': str(OUTPUT / 'launchd.log'),
        'StandardErrorPath': str(OUTPUT / 'launchd.err'),
        'ProcessType': 'Background',
    }


def manage_schedule(action='status'):
    domain = f'gui/{os.getuid()}'
    service = f'{domain}/{LABEL}'
    if action == 'install':
        # launchd의 달력 시각은 시스템 시간대를 사용한다.
        if datetime.now().astimezone().utcoffset() != datetime.now(SEOUL).utcoffset():
            raise RuntimeError('시스템 시간대를 Asia/Seoul로 설정해야 오전 11시 예약이 정확합니다.')
        if not shutil.which('codex'):
            raise RuntimeError('Codex CLI 설치 및 codex login이 필요합니다.')
        subprocess.run(['codex', 'login', 'status'], check=True, capture_output=True)
        OUTPUT.mkdir(parents=True, exist_ok=True)
        PLIST.parent.mkdir(parents=True, exist_ok=True)
        if PLIST.exists():
            subprocess.run(['launchctl', 'bootout', service], capture_output=True)
        with PLIST.open('wb') as stream:
            plistlib.dump(schedule_config(), stream)
        subprocess.run(['launchctl', 'bootstrap', domain, str(PLIST)], check=True, capture_output=True)
        subprocess.run(['launchctl', 'enable', service], check=True, capture_output=True)
        print(f'수익화 조사 예약 등록: 한국 시간 월~금 11:00 (공휴일 제외)\n{PLIST}')
    elif action == 'uninstall':
        subprocess.run(['launchctl', 'bootout', service], capture_output=True)
        if PLIST.exists():
            PLIST.unlink()
        print('수익화 조사 예약을 해제했습니다.')
    else:
        result = subprocess.run(['launchctl', 'print', service], capture_output=True, text=True)
        print(f'수익화 예약: {"활성" if result.returncode == 0 else "미등록"}\n'
              f'설정: {PLIST}\n로그: {OUTPUT}')
