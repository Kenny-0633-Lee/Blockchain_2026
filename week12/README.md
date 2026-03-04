# 12주차 실습 가이드 — ethers.js 스마트 컨트랙트 연동

**경북대학교 블록체인 기술 | ICAB0203-001**

> 🖥️ **실습실 환경: Windows 10/11 + PowerShell**

---

## 학습 목표

- ethers.js v6의 핵심 객체: `Provider` / `Signer` / `Contract`
- 읽기(view) vs 쓰기(transaction) 함수 호출 방식 차이
- `tx.wait()` — 트랜잭션 확인 대기 및 영수증 분석
- 이벤트 리스너(`contract.on()`) 실시간 이벤트 수신

---

## 실행 순서 (PowerShell 창 2개 사용)

### PowerShell 창 1 — 로컬 노드 실행 (계속 유지)

```powershell
cd Blockchain_2026\week12
npm install
npx hardhat node
# 로컬 네트워크 실행 중... (이 창은 종료하지 마세요)
```

### PowerShell 창 2 — 컴파일 + 배포

```powershell
cd Blockchain_2026\week12
npx hardhat compile
npx hardhat run scripts\deploy.js --network localhost
# → 출력된 컨트랙트 주소를 복사해두세요
```

### .env 파일 작성 (week12 폴더)

VS Code 또는 메모장으로 `week12\.env` 파일 생성:
```
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

> 위 주소를 배포 시 출력된 실제 주소로 교체하세요.
> 로컬 Hardhat에서 첫 번째 배포라면 위 기본 주소와 동일할 수 있습니다.

### PowerShell 창 2 — interact.js 실행

```powershell
node scripts\interact.js
```

> 📌 **OS 공통 실행 방법** — `dotenv`가 `.env`를 자동 로드하므로
> Windows / macOS 모두 동일한 명령으로 실행합니다.
> (기존의 `CONTRACT_ADDRESS=0x... node scripts\interact.js` 형식은
> Windows PowerShell에서 동작하지 않으므로 `.env` 파일 방식을 사용합니다.)

---

## 핵심 코드 개념

```javascript
// Provider: 블록체인 읽기 전용 연결
const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");

// Signer: 트랜잭션 서명 가능한 지갑
const signer = new ethers.Wallet(PRIVATE_KEY, provider);

// Contract: 스마트 컨트랙트 인스턴스
const contract = new ethers.Contract(ADDRESS, abi, signer);

// Read — view 함수, 가스 없음
const value = await contract.getNumber();

// Write — 트랜잭션, 가스 사용
const tx = await contract.setNumber(777n);
const receipt = await tx.wait();   // 블록 포함 대기

// 이벤트 수신
contract.on("NumberSet", (by, value) => {
    console.log(`NumberSet: ${value}`);
});
```

---

## 예상 출력

```
=======================================================
  12주차 — ethers.js 스마트 컨트랙트 연동 실습
=======================================================

1. Provider 연결 (로컬 Hardhat 네트워크)
   Chain ID: 31337

2. Signer 설정
   지갑 주소: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
   잔액: 9999.999... ETH

3. Contract 연결
   주소: 0x5FbDB2315678afecb367f032d93F642f64180aa3

4. 이벤트 리스너 등록

5. 읽기 함수 호출 (view)
   현재 저장값: 42

6. 쓰기 함수 호출 (setNumber)
   setNumber(777) 호출 중...
   TX 해시: 0x3f2a...
   ✅ 블록 번호: 2
   ✅ 가스 사용: 43956 gas

7. 변경 후 값 확인
   현재 저장값: 777

   📢 이벤트 수신: NumberSet
      호출자: 0xf39Fd6...
      새 값:  777
```

---

## 프로젝트 구조

```
week12\
├── contracts\SimpleStorage.sol   ← 연동 대상 컨트랙트
├── scripts\deploy.js             ← 배포 스크립트
├── scripts\interact.js           ← ethers.js 연동 실습
├── hardhat.config.js             ← 네트워크 설정 (dotenv 포함)
├── package.json                  ← Node.js 의존성
└── .env                          ← CONTRACT_ADDRESS 기록 (직접 생성)
```

---

## 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| `artifacts 없음` 오류 | `npx hardhat compile` 먼저 실행 |
| `connection refused` | PowerShell 창 1에서 `npx hardhat node` 실행 중인지 확인 |
| 이벤트 수신 안 됨 | 잠시 대기 (1초 timeout 설정됨) |
| `Cannot find module 'dotenv'` | `npm install` 재실행 |

---

## Speed Run Ethereum 소개

https://speedrunethereum.com

학기 후 자율 심화 학습 권장 경로:
1. 🏗 Challenge 0: Simple NFT
2. 🏵 Challenge 1: Decentralized Staking
3. 🎲 Challenge 3: Dice Game
4. 🛡 Challenge 4: DEX

---

## 제출

`node scripts\interact.js` 실행 결과 **전체 스크린샷** → LMS 12주차 제출함

📸 스크린샷: `Win + Shift + S` → 영역 드래그 캡처

---

*v0.3 | 2026-03-04*
