# 13주차 실습 가이드 — KNU Token (ERC-20) 발행

**경북대학교 블록체인 기술 | ICAB0203-001**

---

## 학습 목표

- ERC-20 표준: 6개 필수 함수 + 2개 이벤트 구조
- OpenZeppelin ERC20 + Ownable 상속으로 안전한 토큰 구현
- `decimals()` = 18의 의미: 1 KNUT = 10^18 wei 단위
- `approve` / `transferFrom` 패턴 — DeFi의 핵심 메커니즘
- MetaMask에 커스텀 토큰 추가

---

## 도구 준비

- Remix IDE: https://remix.ethereum.org
- MetaMask: Sepolia Testnet 전환 확인

---

## STEP 1 — Remix에 코드 붙여넣기

1. Remix → `+` → `KNUToken.sol`
2. `week13/KNUToken.sol` 내용 복사 후 붙여넣기

---

## STEP 2 — 컴파일

1. Solidity Compiler → 버전 **0.8.20**
2. **Compile KNUToken.sol**
3. OpenZeppelin 라이브러리를 GitHub에서 자동 다운로드 (30초~1분 소요)
4. ✅ 녹색 체크 확인

---

## STEP 3 — Sepolia 배포

1. Deploy & Run → Environment: **Injected Provider - MetaMask**
2. Contract: `KNUToken`
3. Deploy 옆 입력란:
   ```
   initialSupply: 1000000
   ```
   (100만 KNUT 초기 발행)
4. **Deploy** → MetaMask 승인
5. 컨트랙트 주소 메모

---

## STEP 4 — 함수 호출 실습

**읽기 (파란 버튼):**

| 함수 | 입력 | 예상 결과 |
|------|------|----------|
| `name()` | 없음 | "KNU Token" |
| `symbol()` | 없음 | "KNUT" |
| `decimals()` | 없음 | 18 |
| `totalSupply()` | 없음 | 1000000000000000000000000 (10^24) |
| `balanceOf` | 내 주소 | 같은 값 |
| `balanceOfKNUT` | 내 주소 | 1000000 |

**쓰기 (주황 버튼):**

| 함수 | 입력 | 설명 |
|------|------|------|
| `transfer` | `교수님주소, 1` | 1 KNUT 전송 (단위 주의: 10^18 곱해야 함) |
| `mint` | `내주소, 1000` | 1000 KNUT 추가 발행 (owner만) |
| `burn` | `100` | 100 KNUT 소각 |

> ⚠️ `transfer` 의 amount는 **wei 단위**: 1 KNUT = 1000000000000000000

---

## STEP 5 — MetaMask에 KNUT 추가

1. MetaMask → Assets → **Import Tokens**
2. Token Contract Address: 배포한 컨트랙트 주소
3. Symbol: KNUT / Decimals: 18
4. KNUT 잔액 확인

---

## STEP 6 — 교수님 주소로 KNUT 전송

```
교수님 Sepolia 주소: 0x21d9795E987694a2a8E1ad7FF2250c953D166896
전송량: 1 KNUT 이상
```

Remix에서:
```
transfer(
  to: 0x21d9795E987694a2a8E1ad7FF2250c953D166896,
  amount: 1000000000000000000   ← 1 KNUT = 10^18
)
```

또는 MetaMask에서 Send → KNUT 선택

---

## ERC-20 approve/transferFrom 패턴 이해

```
시나리오: DeFi DEX가 내 토큰을 대신 스왑하는 경우

1. approve(DEX주소, 100 KNUT)  → "DEX가 내 100 KNUT를 쓸 수 있도록 허용"
2. DEX.swap() 호출              → DEX 내부에서 transferFrom(나, 풀, 100 KNUT) 실행
3. allowance(나, DEX) = 0     → 허용량 소진
```

Remix에서 직접 실험:
1. `approve(다른주소, 1000000000000000000)` — 1 KNUT 승인
2. `allowance(내주소, 다른주소)` — 승인량 확인

---

## 토의 질문

1. `decimals()` = 18인 이유는 무엇인가요? (힌트: ETH의 최소 단위)
2. `approve` + `transferFrom` 없이 DeFi가 어떻게 작동할 수 있나요?
3. `MAX_SUPPLY`를 설정하는 경제적 이유는 무엇인가요?

---

## 제출

1. Sepolia Etherscan에서 컨트랙트 주소 확인 스크린샷
2. 교수님 주소로 KNUT 전송 트랜잭션 해시

→ LMS 13주차 제출함 업로드

---

*v0.1 | 2026-03-04*
