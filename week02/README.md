# 2주차 실습 가이드 — 개발 환경 구축

**경북대학교 블록체인 기술 | ICAB0203-001**

> 🖥️ **실습실 환경: Windows 10/11 + PowerShell**
> 개인 Mac 사용자는 맨 아래 [macOS 참고](#macos-참고-개인-노트북) 섹션을 보세요.

---

## 최종 목표 — PowerShell에서 아래 5개 모두 버전 출력

```powershell
git --version      # git version 2.x.x.windows.x
uv --version       # uv 0.x.x
code --version     # 1.9x.x
node --version     # v20.x.x 이상
npm --version      # 10.x.x 이상
```

---

## STEP 1 — Git 설치

**다운로드:** https://git-scm.com/download/win
→ **64-bit Git for Windows Setup** 클릭 → 모든 옵션 기본값으로 설치

**PowerShell에서 설치 확인:**
```powershell
git --version
```

**최초 설정 (1회만):**
```powershell
git config --global user.name "본인이름"
git config --global user.email "학번@knu.ac.kr"
```

---

## STEP 2 — uv 설치 (Python 환경 관리자)

> `uv`는 Python 버전 관리 + 가상환경 + 패키지 설치를 통합한 도구입니다.
> 이 강의의 **모든 Python 실습은 `uv run python ...` 으로 실행**합니다.

**PowerShell에서 설치:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> ⚠️ **"이 시스템에서 스크립트를 실행할 수 없습니다" 오류 시**
> PowerShell을 **관리자 권한**으로 열고 먼저 실행 후 재시도:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**PowerShell 새 창**을 열고 설치 확인:
```powershell
uv --version
```

**저장소 클론 + 가상환경 자동 구성:**
```powershell
git clone https://github.com/Kenny-0633-Lee/Blockchain_2026.git
cd Blockchain_2026
uv sync
```

> 📌 `uv sync`는 `pyproject.toml`을 읽어 Python + 가상환경 + 패키지를 한 번에 설치합니다.

**환경 구축 확인:**
```powershell
uv run python -c "import cryptography, ecdsa, base58; print('환경 구축 완료!')"
```

---

## STEP 3 — VS Code 설치

**다운로드:** https://code.visualstudio.com/
→ **Windows x64** 선택 → 설치 중 **"Add to PATH"** 옵션 반드시 체크 ✅

**PowerShell에서 설치 확인:**
```powershell
code --version
```

> ⚠️ `'code'은(는) 내부 또는 외부 명령... 아닙니다` 오류 시:
> VS Code 실행 → `Ctrl+Shift+P` → `Shell Command: Install 'code' command in PATH` 실행 → PowerShell **새 창** 열기

**필수 확장 플러그인 설치 (`Ctrl+Shift+X`):**

| 확장명 | 용도 |
|--------|------|
| `ms-python.python` | Python 실습 |
| `charliermarsh.ruff` | 코드 스타일 |
| `juanblanco.solidity` | Solidity 문법 강조 |

**프로젝트 열기 + Python 인터프리터 설정:**
```powershell
cd Blockchain_2026
code .
```
VS Code 하단 상태바 → Python 버전 클릭 → `.venv\Scripts\python.exe` 선택
또는 `Ctrl+Shift+P` → `Python: Select Interpreter` → `.venv` 항목 선택

---

## STEP 4 — Node.js 설치

> 지금 설치만 해두고 실제 사용은 **11주차(Hardhat)**부터입니다.

**다운로드:** https://nodejs.org/en → **LTS (20.x)** 선택 → 기본값으로 설치

**설치 후 PowerShell 새 창**을 열고 확인:
```powershell
node --version   # v20.x.x 이상
npm --version    # 10.x.x 이상
```

> ⚠️ 설치 직후 반드시 PowerShell **새 창**을 열어야 PATH가 반영됩니다.

---

## 최종 검증 — 5개 한 번에 실행

```powershell
git --version; uv --version; code --version; node --version; npm --version
```

모두 버전 번호가 출력되면 완료입니다. 📸

**스크린샷 제출:** `Win + Shift + S` → 영역 드래그 캡처 → LMS 2주차 제출함

---

## 실습 코드 실행 확인 (3주차 예습)

```powershell
cd Blockchain_2026
uv run python week03\merkle_tree.py
```

> 📌 Windows에서 경로 구분자는 `\` 또는 `/` 모두 사용 가능합니다.

---

## 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| `이 시스템에서 스크립트를 실행할 수 없습니다` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` 후 재시도 |
| `uv` 명령을 찾을 수 없음 | PowerShell **새 창** 열기 (PATH 반영) |
| `git` 명령을 찾을 수 없음 | PowerShell 새 창 또는 PC 재시작 |
| `code` 명령을 찾을 수 없음 | VS Code → `Ctrl+Shift+P` → "Install 'code' command in PATH" |
| `node` 명령을 찾을 수 없음 | PowerShell **새 창** 열기 |
| Python 인터프리터 미선택 | `Ctrl+Shift+P` → "Python: Select Interpreter" → `.venv` 선택 |
| `uv sync` 네트워크 오류 | 핫스팟 전환 후 재시도 |

---

## macOS 참고 (개인 노트북)

> 실습실은 Windows입니다. 아래는 개인 Mac 사용자만 참고하세요.

```bash
# Git: 터미널에서 git 입력 시 자동 설치 안내
xcode-select --install

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js
brew install node@20
# 또는 nodejs.org에서 .pkg 다운로드

# VS Code: code.visualstudio.com → .dmg 다운로드
# code 명령어 등록: Cmd+Shift+P → "Install 'code' command in PATH"

# 스크린샷: Cmd+Shift+4
```

---

*v0.3 | 2026-03-04*
