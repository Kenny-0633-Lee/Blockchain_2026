# 9주차 실습 가이드 — Ethereum + MetaMask: 가스 시스템 심화

**경북대학교 블록체인 기술 | ICAB0203-001**

> 이번 주는 Python 코드 없음 — MetaMask와 Sepolia Etherscan을 직접 활용합니다.

---

## 학습 목표

- EVM(Ethereum Virtual Machine) 구조와 가스 개념
- `gasLimit` vs `gasUsed` vs `gasPrice` vs `baseFee` vs `priorityFee` 구분
- EIP-1559 수수료 모델 이해 (Base Fee + Priority Fee)
- Sepolia에서 직접 트랜잭션을 전송하고 가스 비용 분석

---

## 사전 준비

- MetaMask 설치 및 Sepolia Testnet 설정 (1주차 완료)
- Sepolia ETH 잔액 확인 (없으면 Faucet에서 보충)

**Faucet:**
```
https://sepoliafaucet.com
https://faucet.quicknode.com/ethereum/sepolia
```

---

## STEP 1 — MetaMask 가스 설정 이해

MetaMask → Send → 수취인 주소 입력 → Amount 입력 → **다음**

**Gas 설정 화면:**

| 항목 | 의미 |
|------|------|
| **Gas Limit** | 이 TX에 허용하는 최대 가스 단위 (단순 전송 = 21,000) |
| **Base Fee** | 네트워크가 결정한 최소 가스 가격 (소각됨) |
| **Priority Fee** | 채굴자/검증자에게 주는 팁 (빠른 처리 유도) |
| **Max Fee** | 내가 지불할 최대 가스 가격 (Max Fee ≥ Base Fee + Priority Fee) |

---

## STEP 2 — 트랜잭션 전송 실험

**실험 A: 낮은 수수료 vs 높은 수수료**

1. MetaMask → Send to 교수님 주소:
   ```
   0x21d9795E987694a2a8E1ad7FF2250c953D166896
   ```
2. Amount: 0.0001 ETH
3. **Edit Gas** 클릭 → Priority Fee를 각각 설정:

| 실험 | Priority Fee | 예상 결과 |
|------|-------------|----------|
| A-1 | 0.001 Gwei | 매우 느림 (Mempool 대기) |
| A-2 | 1 Gwei (권장) | 보통 속도 |
| A-3 | 5 Gwei 이상 | 빠른 처리 |

---

## STEP 3 — Etherscan에서 가스 분석

트랜잭션 전송 후 TXID를 Sepolia Etherscan에서 분석:

```
https://sepolia.etherscan.io/tx/[TXID]
```

**확인할 항목:**

| 항목 | 예시값 | 의미 |
|------|--------|------|
| Gas Limit | 21,000 | 설정한 최대 가스 |
| Gas Used | 21,000 | 실제 사용 가스 |
| Base Fee Per Gas | 0.xx Gwei | EIP-1559 기본 수수료 |
| Max Priority Fee | 1 Gwei | 팁 |
| Transaction Fee | 0.000021 ETH | 실제 지불 수수료 |

---

## STEP 4 — 가스 계산 실습

아래 공식으로 수수료를 직접 계산해보세요:

```
수수료(ETH) = Gas Used × (Base Fee + Priority Fee)
            = 21,000 × (Base Fee + Priority Fee) × 10^-18

예시:
  Gas Used = 21,000
  Base Fee = 10 Gwei = 10 × 10^-9 ETH
  Priority Fee = 1 Gwei = 1 × 10^-9 ETH
  수수료 = 21,000 × 11 × 10^-9 = 0.000231 ETH
```

**나의 실제 트랜잭션 계산표:**

| 항목 | 내 TX 값 |
|------|---------|
| Gas Used | |
| Base Fee (Gwei) | |
| Priority Fee (Gwei) | |
| 계산 수수료 (ETH) | |
| Etherscan 표시 수수료 | |
| 일치 여부 | |

---

## STEP 5 — EIP-1559 이해

**EIP-1559 이전 (legacy):**
```
수수료 = Gas Limit × Gas Price (경매 방식)
```

**EIP-1559 이후 (2021년 8월, London Hard Fork):**
```
수수료 = Gas Used × (Base Fee + Priority Fee)
Base Fee: 자동 조정 (블록 50% 이상 찼으면 증가, 미만이면 감소)
Base Fee: 소각(Burn) → ETH 디플레이션 효과
Priority Fee: 검증자 수령
```

**Base Fee 소각의 의미:**
- 네트워크가 바쁠수록 ETH가 더 많이 소각됨
- 발행량 vs 소각량에 따라 ETH가 디플레이션 자산이 될 수 있음

---

## 토의 질문

1. Gas Limit을 21,000 미만으로 설정하면 어떤 일이 발생하나요?
2. Base Fee가 소각되는 이유와 이것이 ETH 가치에 미치는 영향은?
3. Mempool에서 트랜잭션이 오래 대기하는 이유와 해결 방법은?

---

## 제출

Sepolia Etherscan 트랜잭션 상세 화면 **스크린샷** (Gas 분석 항목 포함) → LMS 9주차 제출함

---

*v0.1 | 2026-03-04*
