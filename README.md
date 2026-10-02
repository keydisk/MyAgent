# 🤖 MyAgent: macOS 지능형 자율 에이전트 시스템

macOS 환경에 특화된 지능형 자동화 에이전트 시스템입니다.  
**AppleScript 기반 채용 메일 모니터링/요약 창**, **PaceSnap(PhotoAndActivitiesApp) 일일 개선 아이디어 PDF 리포트 및 지시 콘솔**, **평일 오전 11시 자동 스케줄링**, **GitHub 원격 연동** 기능을 갖추고 있으며, 새로운 에이전트를 모듈식으로 손쉽게 추가할 수 있도록 설계되었습니다.

---

## 📁 프로젝트 구조

모든 기능은 독립된 하위 폴더로 구성되어 있으며, `main.py`의 **Command Registry**를 통해 유기적으로 확장됩니다.

```text
/Users/juyoungchoi/Documents/Project/MyAgent/
├── main.py                     # 통합 오케스트레이터 및 확장 가능한 CLI/인터랙티브 실행기
├── requirements.txt            # 시스템 환경 및 의존성 안내
├── README.md                   # 시스템 사용 설명서
├── instructions_log.json       # 사용자가 창에서 입력한 지시사항 히스토리 로그
├── PENDING_INSTRUCTION.md      # 최신 접수된 지시사항 (에이전트 실시간 감지용)
├── output/                     # 생성된 PDF 리포트 및 로그 저장 디렉터리
│   └── PaceSnap_Improvement_Ideas_YYYYMMDD.pdf
│
├── job_mail_agent/             # 📬 기능 1: 채용 메일 & 링크 요약 팝업 에이전트
│   ├── mail_fetcher.py         # AppleScript 기반 Mail.app 최근 메일 수집 및 채용 키워드 필터링
│   ├── mail_analyzer.py        # MIME 디코딩, 본문 요약, 웹 링크 추출 및 실시간 크롤링 요약
│   ├── mail_ui.py              # macOS 스타일 카드형 GUI 창 (메일별 요약 + 링크 요약 + 바로열기)
│   └── run.py                  # 단독 실행 모듈
│
├── project_ideator_agent/      # 🏃‍♂️ 기능 2 & 3: PaceSnap 개선 아이디어 PDF & 지시 콘솔
│   ├── project_analyzer.py     # PhotoAndActivitiesApp 소스 코드, 기획서, 아키텍처 스캔
│   ├── idea_generator.py       # 최신 iOS 17/18, HealthKit, MapKit, 러닝 트렌드 기반 아이디어 5선 도출
│   ├── pdf_generator.py        # Apple 스타일 화이트 테마 HTML 렌더링 -> Chrome Headless 고품질 PDF 변환
│   ├── ideator_ui.py           # PDF 뷰어 연동 + 지시사항 입력 및 접수 GUI 창
│   ├── schedule_manager.py     # macOS launchd 기반 평일(월~금) 오전 11:00 정각 자동 실행 스케줄러
│   └── run.py                  # 단독 실행 모듈
│
└── github_manager/             # 🐙 기능 4: Git 및 GitHub 연동 관리자
    └── git_service.py          # 로컬 git init, commit, gh CLI 기반 원격 저장소 생성 및 push
```

---

## 🚀 빠른 시작

### 1. 인터랙티브 대화형 메뉴로 실행
터미널에서 아무 인자 없이 실행하면 번호를 골라 간편하게 실행할 수 있는 메뉴가 나타납니다.
```bash
python3 main.py
```

### 2. 하위 명령어 직접 실행

#### ① 채용 메일 모니터링 & 링크 요약 창 띄우기
macOS Mail.app을 조회하여 채용 관련 메일(사람인, 원티드, 플렉스웍 등)을 선별하고, 본문과 포함된 링크 웹페이지를 크롤링하여 세련된 팝업 창으로 띄웁니다.
```bash
python3 main.py check-mail
```

#### ② PhotoAndActivitiesApp 개선 아이디어 PDF 생성 & 지시 창 열기
`/Users/juyoungchoi/Documents/Project/PhotoAndActivitiesApp` 프로젝트를 정밀 분석하고, 고화질 PDF 리포트를 생성하여 기본 PDF 뷰어로 띄움과 동시에 **사용자 지시 입력 창**을 실행합니다.
```bash
python3 main.py ideate
```

#### ③ 평일(월~금) 오전 11:00 자동 실행 스케줄 등록
macOS 네이티브 `launchd` 데몬에 등록하여 컴퓨터가 켜져 있을 때 매주 평일 오전 11시 정각에 자동으로 위 아이디어 리포트와 창을 띄웁니다.
```bash
# 상태 확인
python3 main.py schedule-ideator status

# 평일 오전 11시 스케줄 활성화 등록
python3 main.py schedule-ideator install

# 스케줄 등록 해제
python3 main.py schedule-ideator uninstall
```

#### ④ 내 GitHub에 변경 사항 커밋 및 푸시
로컬 변경 사항을 커밋하고, 사용자의 GitHub 계정(`keydisk`)에 저장소를 생성 및 연동하여 원격으로 푸시합니다.
```bash
python3 main.py sync-github
```

---

## 💡 주요 기능 상세 안내

### 1. 📬 채용 메일 및 웹 링크 지능형 요약
- **AppleScript 네이티브 연동**: macOS 기본 `Mail.app`의 받은 편지함을 스캔합니다.
- **다국어 및 도메인 키워드 필터링**: 채용, 공고, 모집, 면접, 합격, 개발자, 이직, 사람인, 원티드, 플렉스웍, 이랜서, recruit, hiring 등의 키워드를 정밀 식별합니다.
- **MIME 디코딩 및 리다이렉트 URL 추적**: Quoted-Printable 인코딩을 해석하고 이메일 트래킹 링크에서 실제 채용 공고 원본 웹사이트 주소를 역추적합니다.
- **웹페이지 실시간 스크랩 요약**: 메일에 삽입된 외부 공고 링크의 타이틀과 메타데이터(Description, OpenGraph)를 크롤링하여 요약합니다.
- **카드형 GUI 뷰어**: 이전/다음 메일 넘기기, 핵심 요약 확인, 외부 링크 원클릭 브라우저 열기, Apple Mail 앱 원클릭 열기를 지원합니다.

### 2. 🏃‍♂️ PaceSnap 프로젝트 일일 개선 리포트 & 지시 수신 인터페이스
- **코드베이스 자동 진단**: Tuist 4.x, Clean Architecture, HealthKit, MapKit, Photos 프레임워크와 README에 기재된 개선 과제(예: `ActivitiesView` 메인 내비게이션 연결)를 자동으로 인지합니다.
- **글로벌 러닝 서비스 트렌드 반영**: Strava 연동, 인스타그램 스토리 9:16 다이내믹 페이스 오버레이, Apple Vision 기반 흔들림 없는 인생 샷 선별, Swift 6 Concurrency 대응 등 5대 실전 개선안을 제시합니다.
- **A4 프리미엄 PDF 생성**: Chrome Headless 인쇄 엔진을 활용해 깨짐 없는 고품질 PDF(`output/PaceSnap_Improvement_Ideas_YYYYMMDD.pdf`)를 생성합니다.
- **대화형 제어 콘솔 (지시창)**:
  - 생성된 PDF가 화면에 열림과 동시에 제어 콘솔 창이 팝업됩니다.
  - 5대 아이디어 중 하나를 클릭하면 지시 프롬프트가 자동 완성됩니다.
  - 사용자가 추가 요구사항이나 개선 방향을 입력하고 **[지시 전달 및 작업 접수]** 버튼을 누르면 `PENDING_INSTRUCTION.md` 및 `instructions_log.json`에 저장되어 AI 에이전트가 즉각 작업을 이어받아 구현할 수 있습니다.

### 3. ⏰ 평일 오전 11:00 macOS `launchd` 스케줄링
- macOS의 권장 백그라운드 관리자인 `LaunchAgents`(`com.myagent.ideator.plist`)를 사용하여 평일(월~금) 11:00 AM에 정확하게 실행됩니다.
- 배터리 친화적이며 시스템 재부팅 후에도 정상 유지됩니다.

---

## 🧩 신규 기능 추가 (확장 가이드)

새로운 기능을 추가하려면:
1. `MyAgent/` 아래에 새로운 하위 폴더(예: `slack_bot_agent/`)를 생성합니다.
2. 실행 로직 함수 `run_slack_bot()`을 작성합니다.
3. `main.py`의 `register_command()`에 한 줄만 등록하면 CLI 및 인터랙티브 메뉴에 즉시 반영됩니다:
   ```python
   register_command(
       name="slack-bot",
       handler=lambda args: run_slack_bot(),
       description="슬랙 알림 및 메시지 전송 기능",
       category="알림"
   )
   ```
