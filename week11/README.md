# 11주차 실습 가이드 — Hardhat 로컬 개발 환경

**경북대학교 블록체인 기술 | ICAB0203-001**

> 🖥️ **실습실 환경: Windows 10/11 + PowerShell**

---

## 학습 목표

- Hardhat 프로젝트 구조 이해
- 로컬 Hardhat 네트워크에서 컨트랙트 컴파일 + 배포
- Chai를 이용한 스마트 컨트랙트 자동화 테스트
- 시간 조작(`time.increaseTo`) 등 테스트 헬퍼 활용
- Sepolia 테스트넷에 실제 배포

---

## 사전 준비

PowerShell에서 Node.js 설치 확인:
```powershell
node --version   # v20.x.x 이상
npm --version    # 10.x.x 이상
```

---

## STEP 1 — 의존성 설치

```powershell
cd Blockchain_2026\week11
npm install
```

> 📌 `npm install`은 `package.json`을 읽어 Hardhat + dotenv를 자동 설치합니다.

---

## STEP 2 — 컴파일

```powershell
npx hardhat compile
```

성공 시:
```
Compiled 1 Solidity file successfully (evm target: paris).
```

`artifacts\` 폴더에 ABI + 바이트코드가 생성됩니다.

---

## STEP 3 — 테스트 실행

```powershell
npx hardhat test
```

예상 출력:
```
  Lock
    배포
      ✔ 올바른 잠금 해제 시각 설정
      ✔ 소유자 주소 올바르게 설정
      ✔ 컨트랙트에 ETH 입금 확인
      ✔ 과거 시간으로 배포 시 실패
    인출(withdraw)
      ✔ 잠금 시간 전 인출 시 실패
      ✔ 소유자 아닌 계정으로 인출 시 실패
      ✔ 잠금 시간 후 소유자 인출 성공
      ✔ 인출 시 Withdrawal 이벤트 발생

  8 passing (xxx ms)
```

---

## STEP 4 — 로컬 네트워크 배포

**PowerShell 창 1** — Hardhat 로컬 노드 실행:
```powershell
cd Blockchain_2026\week11
npx hardhat node
# 20개 테스트 계정과 함께 로컬 네트워크 실행 중...
# 이 창은 유지합니다 (종료하지 마세요)
```

**PowerShell 창 2** — 배포 (새 창):
```powershell
cd Blockchain_2026\week11
npx hardhat run scripts\deploy.js --network localhost
```

> 💡 Windows Terminal을 사용하면 탭으로 두 창 관리가 편리합니다.

---

## STEP 5 — Sepolia 배포 (선택)

### .env 파일 생성 (week11 폴더)

VS Code 또는 메모장으로 `week11\.env` 파일 생성:
```
SEPOLIA_RPC_URL=https://rpc.sepolia.org
PRIVATE_KEY=0x여기에_MetaMask_개인키_입력
ETHERSCAN_API_KEY=
```

> ⚠️ MetaMask 개인키 내보내기: MetaMask → 계정 메뉴 → Account details → Show private key
> ⚠️ `.env` 파일은 절대 GitHub에 올리지 마세요 (`.gitignore`에 이미 포함)

### Sepolia 배포

```powershell
npx hardhat run scripts\deploy.js --network sepolia
```

> 📌 `hardhat.config.js`에 `require("dotenv").config()` 가 포함되어 있어
> **Windows에서 별도 환경변수 설정 없이** `.env` 파일을 자동으로 읽습니다.

---

## 프로젝트 구조

```
week11\
├── contracts\Lock.sol      ← 스마트 컨트랙트
├── test\Lock.test.js       ← Chai 자동화 테스트
├── scripts\deploy.js       ← 배포 스크립트
├── hardhat.config.js       ← 네트워크 설정 (dotenv 포함)
├── package.json            ← Node.js 의존성
└── .env                    ← 민감 정보 (직접 생성, Git 제외)
```

---

## Hardhat 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `npx hardhat compile` | Solidity 컴파일 |
| `npx hardhat test` | 자동화 테스트 실행 |
| `npx hardhat node` | 로컬 네트워크 실행 |
| `npx hardhat run scripts\deploy.js --network localhost` | 로컬 배포 |
| `npx hardhat run scripts\deploy.js --network sepolia` | Sepolia 배포 |

---

## 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| `npx : 명령을 찾을 수 없습니다` | `npm install` 먼저 실행 확인 |
| 테스트 실패 (time 관련) | Node.js 버전 확인: `node --version` (v20 이상 필요) |
| Sepolia 배포 시 "no accounts" | `.env`의 `PRIVATE_KEY` 값 확인 (0x 접두사 포함) |
| `Cannot find module 'dotenv'` | `npm install` 재실행 |

---

## 제출

`npx hardhat test` 결과 화면 **스크린샷** (8개 ✔ 모두 표시) → LMS 11주차 제출함

📸 스크린샷: `Win + Shift + S` → 영역 드래그 캡처

---

*v0.3 | 2026-03-04*
