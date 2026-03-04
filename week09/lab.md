# 9주차 실습 가이드 — Ethereum + MetaMask + Gas 시스템 심화

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.9 Ethereum Architecture

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 사용 도구 | MetaMask + Sepolia Etherscan |
| 핵심 개념 | Gas · Nonce · EOA · Contract Account |
| 제출물 | 트랜잭션 TxHash → LMS 업로드 |
| 준비물 | MetaMask 설치 완료 (1주차) + Sepolia ETH 보유 |

---

## 🎯 학습 목표

- Gas 메커니즘: `Gas Limit`, `Gas Price`, `Base Fee`, `Priority Fee`의 의미를 이해한다
- EOA(Externally Owned Account) vs Contract Account의 차이를 설명할 수 있다
- Sepolia Etherscan에서 트랜잭션 상세 정보를 해석한다
- Nonce가 트랜잭션 순서와 이중 지불 방지에서 하는 역할을 이해한다

---

## 🔑 핵심 개념 요약

### Gas 계산 공식

```
트랜잭션 수수료 = Gas Used × (Base Fee + Priority Fee)

단위: Gas → Wei → Gwei → ETH
  1 ETH = 10^18 Wei
  1 Gwei = 10^9 Wei

ETH 전송 기본 Gas: 21,000
스마트 컨트랙트 호출: 21,000 + 연산 비용
```

### EIP-1559 수수료 구조 (London 업그레이드 이후)

| 구성 | 의미 |
|------|------|
| Base Fee | 네트워크 혼잡도에 따라 자동 결정. **소각됨** |
| Priority Fee (Tip) | 채굴자/검증자에게 주는 추가 보상 |
| Max Fee | 지불할 최대 수수료 (Base Fee + Priority Fee 상한) |

### Bitcoin vs Ethereum 비교

| | Bitcoin | Ethereum |
|--|---------|----------|
| 모델 | UTXO | 계좌 기반 (Account) |
| 튜링완전 | ❌ (Script) | ✅ (EVM) |
| 스마트 컨트랙트 | ❌ | ✅ |
| Nonce | TX 입력 고유성 | 계정 TX 순서 카운터 |

---

## ▶ 실습 순서

### STEP 1: MetaMask 설정 확인

1. MetaMask 열기
2. 네트워크: **Sepolia Testnet** 선택 확인
3. 잔액이 0이면 Faucet에서 받기:
   ```
   https://sepoliafaucet.com
   https://faucet.sepolia.dev
   ```

---

### STEP 2: 교수님 주소로 0.001 ETH 전송

```
교수님 Sepolia 주소: 0x21d9795E987694a2a8E1ad7FF2250c953D166896
```

1. MetaMask → `Send`
2. 수신 주소 입력: `0x21d9795E987694a2a8E1ad7FF2250c953D166896`
3. 금액: `0.001 ETH`
4. `Next` → 수수료 확인
5. `Confirm`

---

### STEP 3: Sepolia Etherscan에서 트랜잭션 분석

```
https://sepolia.etherscan.io
```

MetaMask History에서 TxHash 복사 → Etherscan에 검색

**확인 항목:**

| 항목 | 찾는 위치 | 의미 |
|------|-----------|------|
| Transaction Hash | 상단 | 트랜잭션 고유 ID |
| Status | `Success` | 처리 완료 |
| Block | 블록 번호 | 포함된 블록 |
| Nonce | 하단 세부정보 | 이 계정의 몇 번째 TX |
| Gas Price | 하단 | 지불한 Gwei |
| Gas Limit | 하단 | 설정한 최대 Gas |
| Gas Used | 하단 | 실제 사용 Gas (ETH 전송 = 21,000) |
| Base Fee | 하단 | EIP-1559 소각 수수료 |
| Txn Fee | 하단 | 실제 지불 수수료 (ETH) |

---

### STEP 4: 내 계정 Nonce 변화 확인

1. Etherscan에서 내 MetaMask 주소 검색
2. `Transactions` 탭에서 이전 TX 목록 확인
3. 각 TX의 Nonce 값이 0, 1, 2… 순서대로 증가하는지 확인

> 💡 Nonce는 이 계정이 보낸 트랜잭션의 누적 카운터입니다.
> 동일 Nonce는 한 번만 처리되므로 이중 지불이 불가능합니다.

---

### STEP 5: EOA vs Contract Account 차이 확인

1. Etherscan에서 임의의 [이더리움 스마트 컨트랙트 주소] 검색
   - 예: Uniswap V2 Router: `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`
2. `Contract` 탭이 있는지 확인 → Contract Account
3. 내 MetaMask 주소 검색 → `Contract` 탭 없음 → EOA

| | EOA | Contract Account |
|--|-----|-----------------|
| 키 쌍 | 있음 (개인키로 서명) | 없음 |
| 코드 | 없음 | Bytecode 있음 |
| 트랜잭션 시작 | 가능 | 불가 (수동 호출 필요) |
| Nonce | 있음 | 없음 |

---

## ✅ 제출 기준

다음 내용을 LMS에 제출합니다.

- [ ] 트랜잭션 TxHash (64자리 16진수)
- [ ] 스크린샷: Etherscan에서 Gas Used, Nonce가 보이는 화면

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

*9주차 실습 가이드 v0.1 | ICAB0203-001*
