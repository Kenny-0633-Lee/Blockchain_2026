# 10주차 실습 가이드 — Remix IDE: SimpleStorage 스마트 컨트랙트

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.8 Smart Contracts + Ch.11 Tools

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 실습 도구 | Remix IDE (브라우저) |
| 실습 코드 | `week10/SimpleStorage.sol` |
| 핵심 개념 | Solidity 문법 · 컴파일 · 배포 · ABI · 이벤트 |
| 제출물 | 배포 + 함수 호출 스크린샷 → LMS |

---

## 🎯 학습 목표

- Solidity의 기본 구조: 상태변수, 함수, 이벤트, modifier를 이해한다
- Remix IDE에서 컴파일 → 배포 → 함수 호출의 전체 흐름을 익힌다
- `view` / `pure` 함수와 일반 함수의 Gas 차이를 이해한다
- 이벤트(Event) 로그가 트랜잭션 영수증에 어떻게 기록되는지 확인한다

---

## 🔑 핵심 개념 요약

### Solidity 함수 종류

| 종류 | 블록체인 읽기 | 블록체인 쓰기 | Gas | 예시 |
|------|-------------|-------------|-----|------|
| 일반 함수 | ✅ | ✅ | 필요 | `set()`, `reset()` |
| `view` | ✅ | ❌ | 없음 | `get()`, `getInfo()` |
| `pure` | ❌ | ❌ | 없음 | `add()` |

### 이벤트 (Event)

```solidity
event ValueChanged(address indexed by, uint256 oldValue, uint256 newValue);

// 함수 내에서 발생
emit ValueChanged(msg.sender, old, value);
```

- 이벤트는 트랜잭션 영수증의 `Logs`에 기록됨
- `indexed` 매개변수는 검색 필터링 가능
- 블록체인 외부(프론트엔드, 백엔드)에서 구독 가능

### modifier

```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "caller is not the owner");
    _;   // ← 원래 함수 실행 위치
}

function reset() public onlyOwner { ... }
```

---

## ▶ 실습 순서

### STEP 1: Remix IDE 접속

```
https://remix.ethereum.org
```

---

### STEP 2: 파일 생성 및 코드 붙여넣기

1. 왼쪽 파일 탐색기 → `contracts/` 폴더 클릭
2. 새 파일 아이콘 → 파일명: `SimpleStorage.sol`
3. `week10/SimpleStorage.sol` 내용 전체 붙여넣기

---

### STEP 3: 컴파일

1. 왼쪽 사이드바 → **Solidity Compiler** 탭 (S 아이콘)
2. Compiler version: `0.8.20` 선택
3. `Compile SimpleStorage.sol` 클릭
4. ✅ 초록 체크마크 확인 (오류 없으면 정상)

---

### STEP 4: 로컬 배포 (Gas 없이 테스트)

1. 왼쪽 사이드바 → **Deploy & Run Transactions** 탭 (▶ 아이콘)
2. Environment: `Remix VM (Shanghai)` 선택 (로컬 테스트넷)
3. Contract: `SimpleStorage` 확인
4. `Deploy` 클릭
5. 하단 `Deployed Contracts` → 컨트랙트 주소 확인

---

### STEP 5: 함수 호출

배포된 컨트랙트를 클릭하여 펼칩니다.

**쓰기 함수 (주황색 버튼 — Gas 소모):**

```
set(42)     → 값 42 저장
set(100)    → 값 100으로 덮어쓰기
reset()     → owner만 가능, 0으로 초기화
```

**읽기 함수 (파란색 버튼 — Gas 없음):**

```
get()       → 현재 저장값 반환
add(3, 5)   → 8 반환 (블록체인 미참조)
getInfo()   → owner, value, updateCount 반환
owner()     → 배포자 주소 반환
updateCount()  → 업데이트 횟수 반환
```

---

### STEP 6: 이벤트 로그 확인

1. `set(42)` 호출 후 하단 **Terminal** (콘솔) 확인
2. 트랜잭션 클릭 → `logs` 펼치기
3. `ValueChanged` 이벤트 확인:
   - `by`: 호출자 주소
   - `oldValue`: 0
   - `newValue`: 42

---

### STEP 7: (선택) Sepolia 테스트넷 배포

1. MetaMask 연결: Environment → `Injected Provider - MetaMask`
2. MetaMask → Sepolia Testnet 선택 → 연결 승인
3. `Deploy` → MetaMask 팝업 → Confirm
4. Sepolia Etherscan에서 컨트랙트 주소 확인

---

## ✅ 제출 기준

다음이 모두 보이는 스크린샷을 LMS에 제출합니다.

- [ ] 컴파일 성공 (초록 체크마크)
- [ ] `set(42)` 호출 후 `get()` → 42 반환
- [ ] `updateCount()` → 1 이상의 숫자
- [ ] `ValueChanged` 이벤트 로그 확인

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

## 📝 생각해보기

1. `view` 함수는 왜 Gas가 필요 없을까요?
2. `modifier`를 사용하면 어떤 이점이 있나요?
3. 이벤트(Event)와 상태변수(state variable)는 어떻게 다른가요?

---

*10주차 실습 가이드 v0.1 | ICAB0203-001*
