# 12주차 실습 가이드 — ethers.js 컨트랙트 상호작용

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.12 Web3 Development Using Ethereum

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 사용 도구 | Node.js + Hardhat + ethers.js v6 |
| 실습 폴더 | `week12/` |
| 핵심 개념 | ethers.js · Provider · Signer · ABI · 이벤트 구독 |
| 제출물 | 스크립트 실행 결과 스크린샷 → LMS |

---

## 🎯 학습 목표

- Provider(읽기)와 Signer(쓰기)의 차이를 이해한다
- ethers.js로 컨트랙트를 배포하고 함수를 호출한다
- Gas 추정(`estimateGas`)과 트랜잭션 영수증 분석을 수행한다
- 이벤트 로그 조회(`queryFilter`)와 실시간 구독(`.on()`)을 구현한다

---

## 🔑 핵심 개념 요약

### Provider vs Signer

```
Provider (읽기 전용)
  ├── 블록체인 상태 조회
  ├── 잔액, 블록 정보, 이벤트 조회
  └── 트랜잭션 서명 불가

Signer (서명 가능)
  ├── Provider의 모든 기능
  ├── 개인키로 트랜잭션 서명
  └── 트랜잭션 전송 가능
```

### ABI (Application Binary Interface)

```
스마트 컨트랙트 함수의 입출력 명세서
컴파일 후 artifacts/ 폴더에 JSON으로 생성됨
ethers.js가 ABI를 참조하여 JavaScript ↔ EVM 데이터 변환
```

### ethers.js v6 주요 패턴

```javascript
// 컨트랙트 배포
const factory  = await ethers.getContractFactory("SimpleStorage");
const contract = await factory.deploy(initialValue);
await contract.waitForDeployment();

// 읽기 (Gas 없음)
const value = await contract.get();
const value = await contract.get.staticCall();   // 명시적 정적 호출

// 쓰기 (Gas 소모)
const tx      = await contract.set(42n);
const receipt = await tx.wait();   // 트랜잭션 확정 대기

// 이벤트 조회
const events = await contract.queryFilter(contract.filters.ValueChanged());

// 이벤트 실시간 구독
contract.on("ValueChanged", (by, oldVal, newVal) => { ... });
```

---

## ▶ 실습 순서

### STEP 1: 패키지 설치

```bash
cd week12
npm install
```

---

### STEP 2: 컴파일

```bash
npx hardhat compile
```

---

### STEP 3: 스크립트 실행

```bash
npx hardhat run scripts/interact.js
```

PART 1~7 순서대로 실행되며 각 단계 결과를 출력합니다.

---

### STEP 4: 주요 출력 확인

| PART | 확인 항목 |
|------|-----------|
| PART 1 | 네트워크 chainId, 계정 주소, 잔액 |
| PART 2 | 컨트랙트 배포 주소, 바이트코드 크기 |
| PART 3 | `staticCall` 로 Gas 없이 읽기 성공 |
| PART 4 | `set(42)`, `set(100)`, `set(999)` Gas 사용량 |
| PART 5 | `ValueChanged` 이벤트 목록 |
| PART 6 | user1의 `reset()` 실패 (`❌`) 확인 |
| PART 7 | 실시간 이벤트 2개 수신 확인 |

---

## 📝 생각해보기

1. `get()`은 왜 트랜잭션 없이 Gas가 들지 않나요?
2. ABI가 없으면 외부에서 컨트랙트를 어떻게 호출할 수 있을까요?
3. DApp의 프론트엔드에서 MetaMask가 Signer 역할을 한다면, Provider는 무엇이 담당할까요?

---

## ✅ 제출 기준

스크립트 실행 결과에서 다음이 보이는 스크린샷을 LMS에 제출합니다.

- [ ] PART 2: 컨트랙트 배포 주소
- [ ] PART 4: Gas Used 수치
- [ ] PART 6: `❌ 실패 — Unauthorized` 메시지
- [ ] `✅ 12주차 실습 완료` 메시지

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

*12주차 실습 가이드 v0.1 | ICAB0203-001*
