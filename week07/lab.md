# 7주차 실습 가이드 — Electrum Testnet4 + UTXO 실습

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.6 Bitcoin Architecture + Ch.7 Bitcoin in Practice

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 사용 도구 | Electrum (Testnet4 모드) + Mempool.space |
| 핵심 개념 | UTXO · 트랜잭션 구조 · Mempool · Confirmation |
| 제출물 | 전송 TxID (트랜잭션 해시) → LMS 업로드 |
| 준비물 | Electrum 설치 완료 (6주차 말미 안내 참조) |

---

## 🎯 학습 목표

- UTXO(Unspent Transaction Output) 모델을 이해하고 실제로 확인한다
- Electrum 지갑으로 Testnet4 tBTC를 받고 보내는 전체 흐름을 경험한다
- Mempool.space에서 내 트랜잭션의 수명주기를 추적한다
- 트랜잭션 수수료, Confirmation 수와 보안의 관계를 이해한다

---

## 🔑 핵심 개념 요약

### UTXO 모델

```
[이전 TX 출력]          [새 TX 입력]          [새 TX 출력]
Alice의 UTXO: 1.0 BTC  →  Input: 1.0 BTC    →  Bob: 0.5 BTC
                                               →  Alice(잔돈): 0.4999 BTC
                                               →  채굴자 수수료: 0.0001 BTC
```

- 잔액이란 개념 없음 → 내 주소로 들어온 미사용 출력값(UTXO)의 합
- 트랜잭션은 항상 UTXO를 **완전히 소비**하고 잔돈 주소로 돌려받음

### 트랜잭션 수명주기

```
1. 생성 → 2. 서명 → 3. 브로드캐스트 → 4. Mempool 대기
→ 5. 채굴자 선택 → 6. 블록 포함 → 7. Confirmation
```

---

## ▶ 실습 순서

### STEP 1: Electrum Testnet4 모드로 실행

**Windows:**
```
시작 메뉴 → Electrum 우클릭 → "속성" → 대상 란 끝에 추가:
  C:\...electrum-...\electrum.exe --testnet
```

또는 명령 프롬프트:
```cmd
electrum --testnet
```

**macOS:**
```bash
open -a Electrum --args --testnet
```

> ⚠️ 반드시 **--testnet** 옵션을 사용하세요. 없으면 실제 비트코인 네트워크에 연결됩니다.

---

### STEP 2: 새 지갑 생성

1. Electrum 실행 → `Create a new wallet`
2. Wallet type → `Standard wallet`
3. Keystore → `Create a new seed`
4. Seed type → `Segwit`
5. **시드 구문 12단어를 종이에 적어 보관** (분실 시 복구 불가)
6. 지갑 비밀번호 설정 (선택사항)

---

### STEP 3: 내 주소 확인

- 상단 메뉴 → `Receive` 탭
- 주소 확인: **tb1q...** 또는 **m...** 으로 시작하는 Testnet 주소

---

### STEP 4: Testnet4 Faucet에서 tBTC 받기

```
https://mempool.space/testnet4/faucet
```

1. 위 URL 접속
2. 내 Testnet4 주소 입력
3. Send 클릭 → TxID 확인

> 💡 Faucet마다 하루 요청 제한이 있습니다. 여러 Faucet을 시도하세요:
> - https://mempool.space/testnet4/faucet
> - https://coinfaucet.eu/en/btc-testnet4/

---

### STEP 5: Mempool.space에서 트랜잭션 추적

```
https://mempool.space/testnet4
```

1. 내 주소 검색
2. `UTXOs` 탭 → UTXO 목록 확인
3. 트랜잭션 클릭 → Input/Output 구조 확인
4. `Confirmation` 수 확인

---

### STEP 6: 교수님 주소로 tBTC 전송

1. Electrum → `Send` 탭
2. 수신 주소:
   ```
   tb1qwqnjsfm5l4mf3m5n28vpkjd0hvqep5acx8nx97
   ```
3. 금액: `0.0001 tBTC`
4. 수수료: `Normal` 선택
5. `Pay` → 비밀번호 입력 → 전송

---

### STEP 7: 전송 확인

- Electrum → `History` 탭 → 트랜잭션 확인
- `TxID` 복사 (64자리 16진수)
- Mempool.space에서 해당 TxID 검색하여 상태 확인

---

## ✅ 제출 기준

**전송 TxID** (64자리 16진수)를 LMS에 제출합니다.

예시: `a1b2c3d4e5f6...` (64자)

> 📌 Mempool.space에서 TxID를 검색했을 때 트랜잭션이 보여야 합니다.

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

## 🔴 트러블슈팅

| 증상 | 해결 |
|------|------|
| Electrum이 Mainnet으로 연결됨 | `--testnet` 옵션 확인 |
| Faucet 요청 실패 | 다른 Faucet 사이트 시도 |
| 트랜잭션 오래 미확인 | 수수료를 `High`로 올려서 재전송 |
| 주소가 1로 시작 | Testnet 모드 미적용. 재시작 |

---

*7주차 실습 가이드 v0.1 | ICAB0203-001*
