# 1주차 실습 가이드 — MetaMask + Sepolia ETH 체험

**경북대학교 블록체인 기술 | ICAB0203-001**

> 🖥️ **실습실 환경: Windows 10/11 + PowerShell**
> 교수용 ETH 배포 스크립트 (2-file Set / 단일 Set) 안내 포함

---

## 학생 실습 — MetaMask 설치 및 ETH 수신

### STEP 1 — MetaMask 설치 (Chrome 확장)

1. Chrome 웹스토어에서 **MetaMask** 검색 및 설치
2. **Create a new wallet** → 비밀번호 설정
3. 시드 구문(12단어) **종이에 필기** 후 안전 보관

### STEP 2 — Sepolia Testnet 네트워크 추가

MetaMask → 네트워크 선택 → **Add a network manually**:

| 항목 | 값 |
|------|-----|
| 네트워크 이름 | Sepolia Testnet |
| RPC URL | `https://rpc.sepolia.org` |
| 체인 ID | `11155111` |
| 통화 기호 | ETH |
| 블록 탐색기 | `https://sepolia.etherscan.io` |

### STEP 3 — 지갑 주소 제출

MetaMask 상단 주소 클릭 → 복사 → 교수님 제출 폼에 입력

> 주소 형식: `0x` 로 시작하는 42자리 16진수

### STEP 4 — ETH 수신 확인

```
https://sepolia.etherscan.io/address/[내 주소]
```

### 📝 과제

MetaMask 잔액 0.1 ETH + Etherscan 트랜잭션 확인 **스크린샷** → LMS 1주차 제출함

📸 스크린샷: `Win + Shift + S` → 영역 드래그 캡처

---

## 교수용 — ETH 배포 스크립트

> ⚠️ 아래 내용은 **교수님만** 실행합니다.

### 파일 구성

```
week01\
├── 2_1_convert.py       [기존 Set] STEP 1: Tally CSV → students.json 변환
├── 2_2_distribute.py    [기존 Set] STEP 2: students.json → ETH 일괄 전송
├── distribute_eth.py    [단일 Set] CSV 변환 + ETH 배포 통합 (All-in-One)
├── students.json        샘플 (실제 데이터는 00_Admin_Only\ 에 보관)
└── README.md

00_Admin_Only\           ← .gitignore 로 GitHub 추적 제외
├── students_raw.csv     Tally 수출 CSV
└── students.json        변환 후 배포 결과 (tx_hash 포함)
```

### 두 Set 비교

| 항목 | 기존 Set (2_1 + 2_2) | 단일 Set (distribute_eth.py) |
|------|---------------------|------------------------------|
| **구조** | 단계별 분리 | 통합 1 파일 |
| **권장 상황** | 단계마다 확인·수정 필요 시 | 한 번에 빠르게 실행 시 |
| CSV 변환 | `2_1_convert.py` 별도 실행 | `--from-csv` 옵션 |
| 주소 유효성 검사 | ✅ | ✅ |
| 중복 주소 감지 | ✅ | ✅ |
| 재실행 안전성 (status skip) | ✅ | ✅ |
| tx마다 즉시 저장 | ✅ | ✅ |
| **dry-run** | ✅ `--dry-run` | ✅ `--dry-run` |
| 가스비 1.2× 가산 | ✅ | ✅ |

---

### 사전 준비

**패키지 설치 (PowerShell):**
```powershell
cd Blockchain_2026
uv add web3 python-dotenv
```

**`.env` 파일 생성** — 프로젝트 루트(`Blockchain_2026\.env`):

VS Code 또는 메모장으로 생성:
```
INFURA_URL=https://sepolia.infura.io/v3/여기에_PROJECT_ID
PRIVATE_KEY=0x여기에_교수님_개인키
```

> 📌 `.env` 파일은 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다.

---

### 기존 Set 실행 방법 (PowerShell)

```powershell
# 1. Tally CSV를 00_Admin_Only\ 에 저장 후:

# 2. CSV → JSON 변환 (주소 유효성 검사 + 중복 감지 포함)
uv run python week01\2_1_convert.py

# 3. 배포 전 dry-run (잔액 확인 + 전송 계획 출력)
uv run python week01\2_2_distribute.py --dry-run

# 4. 실제 배포
uv run python week01\2_2_distribute.py
```

---

### 단일 Set 실행 방법 (PowerShell)

```powershell
# CSV → 변환 → dry-run (한 번에)
uv run python week01\distribute_eth.py --from-csv students_raw.csv --dry-run

# CSV → 변환 → 실제 배포 (전체 파이프라인)
uv run python week01\distribute_eth.py --from-csv students_raw.csv

# 기존 JSON으로 dry-run
uv run python week01\distribute_eth.py --dry-run

# 기존 JSON으로 배포 (중단 후 재실행 안전)
uv run python week01\distribute_eth.py

# 도움말
uv run python week01\distribute_eth.py --help
```

---

### dry-run 출력 예시

```
=======================================================
  🔎  DRY-RUN — 실제 트랜잭션은 전송되지 않습니다
=======================================================
  발신 지갑  : 0x21d9795E987694a2a8E1ad7FF2250c953D166896
  현재 잔액  : 3.2500 ETH
  현재 가스  : 12.34 Gwei  (× 1.2 가산)

  이미 완료  : 3명  (skip 예정)
  전송 예정  : 27명  × 0.1 ETH  = 2.700 ETH 필요

  ✅  잔액 충분  (여유: 0.550 ETH)

  No  이름            지갑 주소(앞 20자)           금액   상태
  ──────────────────────────────────────────────────────────
    1  홍길동          0x21d9795E987694a2a8...   0.1 ETH  ✓ skip
    2  김철수          0x3AbC1234567890aBcD...   0.1 ETH  → 전송
```

---

### 주의 사항

- `00_Admin_Only\` 폴더는 `.gitignore`에 의해 GitHub에 올라가지 않습니다
- 배포 중단 후 재실행 시 `status="success"` 학생은 자동 skip (중복 전송 방지)
- `PRIVATE_KEY`는 절대 코드에 직접 입력하지 마세요 — `.env` 파일로만 관리

---

*v0.3 | 2026-03-04*
