# 14주차 실습 가이드 — KNU NFT (ERC-721) 민팅

**경북대학교 블록체인 기술 | ICAB0203-001**

---

## 학습 목표

- ERC-721 표준: tokenId 기반 대체 불가능 토큰
- ERC-20 vs ERC-721 비교: Fungible vs Non-Fungible
- `tokenURI` → IPFS 메타데이터 → 이미지 연결 과정
- IPFS & Pinata: 탈중앙 파일 저장 개념 이해
- OpenSea Testnet에서 내 NFT 확인

---

## ERC-20 vs ERC-721 비교

| 항목 | ERC-20 (KNUT) | ERC-721 (KNUNFT) |
|------|--------------|-----------------|
| 특성 | Fungible (대체 가능) | Non-Fungible (대체 불가) |
| 식별자 | 없음 (잔액으로 관리) | tokenId (고유 번호) |
| 잔액 | balanceOf = 숫자 | balanceOf = 보유 NFT 수 |
| 이전 | transfer(to, amount) | transferFrom(from, to, tokenId) |
| 메타데이터 | 없음 | tokenURI → JSON → 이미지 |

---

## IPFS & Pinata — 교수 시연 내용

> 학생은 직접 Pinata를 사용하지 않습니다.  
> 교수님이 준비한 **샘플 tokenURI**를 사용하여 민팅에 집중합니다.

**전체 흐름 (교수 시연):**
```
이미지 파일
    ↓ Pinata 업로드
IPFS CID 획득
    ↓ metadata.json 작성 (sample_metadata.json 참고)
Pinata에 JSON 업로드
    ↓
tokenURI = "https://gateway.pinata.cloud/ipfs/[JSON-CID]"
    ↓ 학생에게 공지
mint(내주소, tokenURI) 호출
```

**샘플 tokenURI (수업 전 교수님 공지):**
```
https://gateway.pinata.cloud/ipfs/[수업 당일 공지 CID]
```

---

## STEP 1 — Remix에 코드 붙여넣기

1. Remix → `+` → `KNUNFT.sol`
2. `week14/KNUNFT.sol` 내용 복사 후 붙여넣기

---

## STEP 2 — 컴파일

1. Solidity Compiler → **0.8.20**
2. **Compile KNUNFT.sol**
3. OpenZeppelin 자동 다운로드 (1분 내외)
4. ✅ 녹색 체크 확인

---

## STEP 3 — Sepolia 배포

1. Deploy & Run → **Injected Provider - MetaMask**
2. Contract: `KNUNFT`
3. **Deploy** (생성자 인수 없음)
4. MetaMask 승인 → 컨트랙트 주소 메모

---

## STEP 4 — NFT 민팅

**교수님이 공지한 tokenURI 사용:**

Remix → Deployed Contracts → `mint` 함수:
```
to:       0x내MetaMask주소
tokenURI: https://gateway.pinata.cloud/ipfs/[교수님공지CID]
```

**트랜잭션 승인 후 확인:**

| 함수 | 입력 | 예상 결과 |
|------|------|----------|
| `ownerOf(0)` | 0 | 내 주소 |
| `tokenURI(0)` | 0 | IPFS URL |
| `totalMinted()` | 없음 | 1 |
| `tokensOfOwner` | 내 주소 | [0] |

---

## STEP 5 — OpenSea Testnet 확인

```
https://testnets.opensea.io/assets/sepolia/[컨트랙트주소]/0
```

또는:
1. https://testnets.opensea.io 접속
2. MetaMask 연결 → 프로필 → 내 NFT 확인

> 💡 OpenSea에 반영까지 수 분 소요될 수 있습니다.

---

## 메타데이터 JSON 구조 이해

```json
{
  "name": "KNU NFT #0",
  "description": "...",
  "image": "ipfs://[이미지-CID]",
  "attributes": [
    {"trait_type": "Year",   "value": "2026"},
    {"trait_type": "Course", "value": "ICAB0203-001"}
  ]
}
```

`sample_metadata.json`을 참고하여 직접 작성해볼 수 있습니다.

---

## 토의 질문

1. ERC-721 NFT와 ERC-20 토큰의 가장 큰 기술적 차이는 무엇인가요?
2. 이미지를 직접 컨트랙트에 저장하지 않고 IPFS를 사용하는 이유는?
3. OpenSea 같은 마켓플레이스는 `tokenURI`를 어떻게 읽어 NFT를 표시하나요?

---

## 제출

OpenSea Testnet에서 내 NFT 확인 **스크린샷** (NFT 이미지 + 이름 표시) → LMS 14주차 제출함

---

*v0.1 | 2026-03-04*
