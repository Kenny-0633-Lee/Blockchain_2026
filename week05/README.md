# 5주차 실습 가이드 — BIP-39 + ECDSA + Bitcoin/Ethereum 주소 도출

**경북대학교 블록체인 기술 | ICAB0203-001**

---

## 학습 목표

- BIP-39 니모닉(12단어) → Seed → 개인키 파생 과정 이해
- ECDSA secp256k1 타원 곡선 암호: 개인키 → 공개키
- Bitcoin P2PKH 주소 생성: Hash160 + Base58Check
- Ethereum 주소 생성: Keccak-256 + 20바이트 추출
- ECDSA 서명 생성 및 변조 감지 실험

---

## 패키지 설치 확인

```powershell
cd Blockchain_2026
uv sync
# 또는
uv add ecdsa base58 mnemonic bip-utils
```

---

## 실행

```powershell
uv run python week05/bip39_ecdsa.py
```

> ⚠️ 실행할 때마다 새로운 니모닉이 생성됩니다. **교육용**이므로 실제 자산을 보관하지 마세요.

---

## 단계별 설명

| STEP | 내용 | 핵심 알고리즘 |
|------|------|--------------|
| **1** | BIP-39 니모닉 생성 | PBKDF2-SHA512 (2048 iterations) |
| **2** | ECDSA 키 쌍 | secp256k1: y²=x³+7 타원 곡선 |
| **3** | Bitcoin 주소 | SHA-256 → RIPEMD-160 → Base58Check |
| **4** | Ethereum 주소 | Keccak-256 → 마지막 20바이트 |
| **5** | 서명 & 검증 | ECDSA sign / verify |

---

## Bitcoin vs Ethereum 주소 비교

| 항목 | Bitcoin | Ethereum |
|------|---------|----------|
| 해시 함수 | SHA-256 + RIPEMD-160 | Keccak-256 |
| 인코딩 | Base58Check | 16진수 (0x 접두사) |
| 형식 | `1ABCd...` (26~35자) | `0x1234...` (42자) |
| BIP-44 경로 | `m/44'/0'/0'/0/0` | `m/44'/60'/0'/0/0` |

---

## 토의 질문

1. 같은 니모닉으로 Bitcoin 주소와 Ethereum 주소가 다른 이유는?
2. 공개키에서 개인키를 알 수 없는 이유를 타원 곡선 관점에서 설명하세요.
3. WIF(Wallet Import Format)는 어떤 용도로 사용되나요?

---

## 제출

터미널 출력 **전체 스크린샷** → LMS 5주차 제출함

---

*v0.1 | 2026-03-04*
