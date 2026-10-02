"""Git 및 GitHub 연동 유틸리티 모듈.
로컬 git 저장소 초기화, 커밋, GitHub 원격 저장소 생성 및 푸시를 자동화합니다.
"""

import os
import subprocess
from typing import Tuple

WORKSPACE_DIR = "/Users/juyoungchoi/Documents/Project/MyAgent"

GITIGNORE_CONTENT = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Logs & temp
output/*.log
output/*.err
output/*.temp.*
output/temp_*
*.log

# IDE
.idea/
.vscode/
"""

def run_cmd(cmd: list, cwd: str = WORKSPACE_DIR) -> Tuple[int, str, str]:
    """명령어 실행 유틸리티"""
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def ensure_gitignore():
    """기본 .gitignore 파일 생성"""
    gi_path = os.path.join(WORKSPACE_DIR, ".gitignore")
    if not os.path.exists(gi_path):
        with open(gi_path, "w", encoding="utf-8") as f:
            f.write(GITIGNORE_CONTENT)
        print("[✓] .gitignore 생성 완료")

def init_local_repo() -> Tuple[bool, str]:
    """로컬 Git 저장소 초기화"""
    git_dir = os.path.join(WORKSPACE_DIR, ".git")
    ensure_gitignore()
    
    if not os.path.exists(git_dir):
        code, out, err = run_cmd(["git", "init", "-b", "main"])
        if code != 0:
            return False, f"git init 실패: {err}"
        print("[✓] git init 완료 (기본 브랜치: main)")
    
    return True, "로컬 git 저장소가 준비되었습니다."

def commit_changes(commit_message: str = "feat: Update MyAgent system and agents") -> Tuple[bool, str]:
    """변경 사항 스테이징 및 커밋"""
    init_local_repo()
    
    # git add .
    code, out, err = run_cmd(["git", "add", "."])
    if code != 0:
        return False, f"git add 실패: {err}"
        
    # 변경 사항이 있는지 확인
    code, status_out, _ = run_cmd(["git", "status", "--porcelain"])
    if not status_out.strip():
        return True, "커밋할 새로운 변경 사항이 없습니다."

    code, out, err = run_cmd(["git", "commit", "-m", commit_message])
    if code != 0:
        return False, f"git commit 실패: {err}"
        
    return True, f"커밋 완료: {commit_message}"

def sync_and_push_repo(repo_name: str = "MyAgent", is_private: bool = False) -> Tuple[bool, str]:
    """
    GitHub 저장소 생성(없는 경우) 및 원격 push 동기화
    GitHub CLI (gh)를 활용합니다.
    """
    ensure_gitignore()
    init_local_repo()
    
    # 1. 커밋 수행
    commit_success, commit_msg = commit_changes("feat: Add JobMailAgent, PaceSnap ProjectIdeator, and Main Orchestrator")
    if not commit_success:
        return False, commit_msg

    # 2. 원격 저장소 설정 확인
    code, remotes, _ = run_cmd(["git", "remote", "-v"])
    has_origin = "origin" in remotes

    if not has_origin:
        print(f"[*] GitHub에 원격 저장소 '{repo_name}' 생성 중...")
        visibility_flag = "--private" if is_private else "--public"
        code, out, err = run_cmd([
            "gh", "repo", "create", repo_name,
            visibility_flag,
            "--source=.",
            "--remote=origin",
            "--push"
        ])
        if code == 0:
            return True, f"GitHub에 새 저장소({repo_name})를 생성하고 성공적으로 푸시했습니다!\n{out}"
        else:
            # 이미 존재하는 저장소인지 확인
            print(f"[!] gh repo create 안내: {err}")
            # 이미 계정에 존재한다면 원격 URL 연결 시도
            remote_url = f"git@github.com:keydisk/{repo_name}.git"
            run_cmd(["git", "remote", "add", "origin", remote_url])

    # 3. 푸시 수행
    print("[*] 원격 저장소(origin main)로 push 중...")
    code, out, err = run_cmd(["git", "push", "-u", "origin", "main"])
    if code == 0:
        return True, f"성공적으로 GitHub에 푸시 완료되었습니다! (origin/main)"
    else:
        # 혹시 원격 브랜치가 비어있지 않은 경우 force나 pull 시도
        return False, f"git push 실패: {err}"

if __name__ == "__main__":
    success, msg = sync_and_push_repo()
    print("결과:", success)
    print("메시지:", msg)
