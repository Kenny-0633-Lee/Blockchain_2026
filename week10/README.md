# 10주차 실습 가이드 — Remix IDE: SimpleStorage.sol 배포

**경북대학교 블록체인 기술 | ICAB0203-001**

---

## 학습 목표

- Solidity 기본 문법: state variable, function, modifier, event
- view 함수(읽기) vs write 함수의 가스 비용 차이
- Remix IDE에서 컴파일 → 배포 → 함수 호출 전 과정 실습
- Sepolia Etherscan에서 이벤트 로그 확인

---

## 도구 준비

- 브라우저: Chrome (MetaMask 확장 설치)
- MetaMask: Sepolia Testnet 전환 확인
- Remix IDE: https://remix.ethereum.org

---

## STEP 1 — Remix에 코드 붙여넣기

1. https://remix.ethereum.org 접속
2. File Explorer → `+` 버튼 → 파일명: `SimpleStorage.sol`
3. GitHub에서 `week10/SimpleStorage.sol` 내용 복사 → 붙여넣기

---

## STEP 2 — 컴파일

1. 좌측 메뉴 **Solidity Compiler** (🔨 아이콘)
2. Compiler 버전: **0.8.20** 선택
3. **Compile SimpleStorage.sol** 버튼 클릭
4. ✅ 녹색 체크 → 컴파일 성공

---

## STEP 3 — 배포

1. 좌측 메뉴 **Deploy & Run Transactions** (📦 아이콘)
2. **Environment**: `Injected Provider - MetaMask`
3. MetaMask 팝업 → Sepolia Testnet 확인 → 연결
4. **Contract**: `SimpleStorage` 선택
5. **Deploy** 옆 입력란에 초기값 입력: `42`
6. **Deploy** 버튼 클릭 → MetaMask 팝업 → 트랜잭션 승인
7. 하단 **Deployed Contracts** 에 컨트랙트 주소 확인

---

## STEP 4 — 함수 호출 실습

**읽기 함수 (파란색 버튼 = 가스 없음):**

| 함수 | 예상 결과 |
|------|----------|
| `getNumber()` | 42 (초기값) |
| `getMessage()` | "Hello, Blockchain!" |
| `getState()` | number, message, owner, count 한번에 |

**쓰기 함수 (주황/빨간색 버튼 = 가스 소비):**

| 함수 | 입력값 | 설명 |
|------|--------|------|
| `setNumber` | `100` | 숫자 변경 |
| `increment` | (없음) | 숫자 +1 |
| `setMessage` | `"경북대 블록체인"` | 메시지 변경 (owner만) |
| `reset` | (없음) | 숫자 0으로 초기화 (owner만) |

---

## STEP 5 — Etherscan에서 확인

컨트랙트 주소로 Etherscan 검색:
```
https://sepolia.etherscan.io/address/[컨트랙트 주소]
```

**확인 항목:**
- Transactions 탭 → 함수 호출 기록
- Events 탭 → `NumberUpdated`, `MessageUpdated` 이벤트 로그
- Contract 탭 → 소스 코드 (Verify 하면 표시됨)

---

## 핵심 개념 정리

```solidity
// State variable: 블록체인에 영구 저장 (SSTORE 명령, 비쌈)
uint256 private storedNumber;

// view function: 읽기만 → 가스 없음
function getNumber() public view returns (uint256) {...}

// write function: 상태 변경 → 트랜잭션, 가스 소비
function setNumber(uint256 _number) public {...}

// modifier: 함수 실행 전 조건 검사
modifier onlyOwner() { require(msg.sender == owner, "..."); _; }

// event: 트랜잭션 로그에 기록 (off-chain에서 구독 가능)
event NumberUpdated(address indexed by, uint256 oldValue, uint256 newValue);
```

---

## 토의 질문

1. `view` 함수를 호출할 때 왜 가스가 들지 않나요?
2. `onlyOwner` modifier가 없다면 어떤 보안 문제가 생기나요?
3. `event`를 사용하는 이유는 무엇인가요? State variable에 저장하는 것과 차이는?

---

## 제출

1. Sepolia Etherscan 컨트랙트 페이지 스크린샷 (주소 + 트랜잭션 목록)
2. Remix에서 `getState()` 호출 결과 스크린샷

→ LMS 10주차 제출함

---

*v0.1 | 2026-03-04*
