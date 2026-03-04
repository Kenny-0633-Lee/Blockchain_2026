# 7주차 실습 가이드 — Electrum Testnet: UTXO & 트랜잭션 구조

**경북대학교 블록체인 기술 | ICAB0203-001**

> 🖥️ **실습실 환경: Windows 10/11**
> Python 코드 없음 — Electrum 지갑 클라이언트를 직접 조작합니다.

---

## 학습 목표

- UTXO(Unspent Transaction Output) 모델 이해
- Bitcoin 주소 유형: P2PKH(Legacy) vs P2SH vs Bech32(SegWit) 비교
- Testnet4 실제 트랜잭션 생성 + Mempool 추적
- Bitcoin 수수료 결정 방식: sats/vByte

---

## 사전 준비 — Electrum 설치 (6주차 말미에 안내, 집에서 미리 설치)

> ⚠️ 반드시 **공식 사이트**에서만 다운로드하세요! 피싱 사이트 주의!

**공식 다운로드:** https://electrum.org/#download
→ **Windows installer (.exe)** 선택 → 기본값으로 설치

---

## Testnet4 모드로 실행하기 (Windows)

### 방법 1 — 명령 프롬프트 (권장, 오류 메시지 확인 가능)

**시작 메뉴**에서 `cmd` 검색 → 명령 프롬프트 실행:

```cmd
"C:\Program Files (x86)\Electrum\electrum-4.5.8.exe" --testnet
```

> 버전 번호(`4.5.8`)는 설치된 버전에 맞게 수정하세요.
> 설치 경로 확인: `C:\Program Files (x86)\Electrum\` 폴더 확인

### 방법 2 — 바탕화면 바로가기 수정

1. 바탕화면의 Electrum 바로가기 → **우클릭 → 속성**
2. **대상(Target)** 란 끝에 ` --testnet` 추가:
   ```
   "C:\Program Files (x86)\Electrum\electrum-4.5.8.exe" --testnet
   ```
3. **확인** 클릭 → 해당 바로가기로 실행

**실행 확인:** Electrum 창 제목에 `[testnet]` 표시되면 정상

> ⚠️ **`[testnet]` 없이 실행하면 Bitcoin Mainnet에 연결됩니다.**
> Mainnet에서 실수로 트랜잭션 전송 시 **실제 금전 손실** 발생!

---

## STEP 1 — Testnet 지갑 생성

1. Electrum 실행 (`[testnet]` 확인)
2. **Create new wallet** → Standard wallet → **Generate new seed**
3. 시드 구문(12단어) **종이에 필기** (교육용 — 실제 자산 보관 금지)
4. 비밀번호 설정 (강의실에서는 빈칸도 무방)

---

## STEP 2 — Testnet4 BTC 받기

내 수신 주소 확인:
```
Addresses 탭 → 첫 번째 주소 복사 (tb1q... 로 시작)
```

Testnet4 Faucet에서 tBTC 요청:

| Faucet | URL |
|--------|-----|
| Mempool Faucet | https://mempool.space/testnet4/faucet |
| Coinfaucet | https://coinfaucet.eu/en/btc-testnet4/ |

수신 확인: https://mempool.space/testnet4/address/[내 주소]

> 📌 수신까지 10~30분 소요됩니다.

---

## STEP 3 — UTXO 분석

**Electrum Coins 탭:**
```
Wallet → Coins  (또는 View 메뉴 → Show Coins)
```

| 컬럼 | 의미 |
|------|------|
| Address | UTXO가 잠긴 주소 |
| Amount | UTXO 금액 (BTC) |
| Height | 포함된 블록 번호 |
| Status | unconfirmed / x confirmations |

**Mempool 탐색기로 UTXO 구조 분석:**
```
https://mempool.space/testnet4/address/[내 주소]
→ UTXO 목록 → 각 트랜잭션 클릭 → inputs / outputs 구조 확인
```

---

## STEP 4 — 교수님 주소로 트랜잭션 전송

교수님 Testnet4 주소:
```
tb1qwqnjsfm5l4mf3m5n28vpkjd0hvqep5acx8nx97
```

**전송 절차:**
1. Send 탭 → **Pay to**: 위 주소 붙여넣기
2. **Amount**: 0.0001 tBTC
3. **Fee**: Recommended 선택 (또는 sats/vByte 직접 입력)
4. **Preview** 클릭 → UTXO 선택 + 잔돈(Change) 주소 확인
5. **Send** → 트랜잭션 해시(TXID) 복사

**Mempool 추적:**
```
https://mempool.space/testnet4/tx/[TXID]
```

---

## 토의 질문

1. 0.005 BTC UTXO 하나로 0.001 BTC 전송 시, UTXO는 어떻게 변하나요?
2. 잔돈(Change)이 내 지갑의 **새 주소**로 나가는 이유는 무엇인가요?
3. 수수료(sats/vByte)를 높이면 어떤 이점이 있나요?
4. SegWit(`tb1q...`) 주소가 Legacy(`m/n...`) 주소보다 유리한 이유는?

---

## 트러블슈팅

| 증상 | 해결 방법 |
|------|----------|
| 창 제목에 `[testnet]` 없음 | `--testnet` 옵션 확인 후 재실행 |
| "Not connected" 표시 | 하단 상태바 클릭 → 서버 자동 선택 대기 |
| Faucet에서 tBTC 수신 안 됨 | 10~30분 대기 + mempool.space/testnet4 에서 주소 확인 |
| exe 경로 오류 | `C:\Program Files (x86)\Electrum\` 폴더에서 .exe 파일명 확인 |

---

## macOS 참고 (개인 노트북)

```bash
# .dmg 다운로드 후 Applications에 복사
# 터미널에서 Testnet 모드 실행:
open -a Electrum --args --testnet
```

---

## 제출

Mempool 트랜잭션 화면 **스크린샷 1장** (TXID + 확인 상태 포함) → LMS 7주차 제출함

📸 스크린샷: `Win + Shift + S` → 영역 드래그 캡처

---

*v0.3 | 2026-03-04*
