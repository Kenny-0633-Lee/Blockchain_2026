# 14주차 실습 가이드 — KNU NFT (ERC-721) 민팅

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.10 & Ch.15 Tokenization (ERC-721 섹션)

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 실습 도구 | Remix IDE + MetaMask (Sepolia) |
| 실습 코드 | `week14/KNUNFT.sol` |
| 핵심 개념 | ERC-721 · tokenId · tokenURI · IPFS · OpenSea |
| 제출물 | OpenSea Testnet에서 내 NFT 확인 스크린샷 → LMS |

---

## 🎯 학습 목표

- ERC-721(NFT) 표준과 ERC-20의 차이를 설명한다
- `tokenId` 기반 소유권 추적 메커니즘을 이해한다
- `tokenURI`와 NFT 메타데이터 JSON 구조를 이해한다
- IPFS를 통한 탈중앙화 파일 저장의 개념을 이해한다
- Remix에서 NFT를 민팅하고 OpenSea Testnet에서 확인한다

---

## 🔑 핵심 개념 요약

### ERC-20 vs ERC-721

| | ERC-20 (대체 가능) | ERC-721 (대체 불가능) |
|--|---|---|
| 단위 | 분할 가능 (0.001 KNUT) | 개별 단위 (tokenId) |
| 고유성 | 없음 (모두 동일) | 있음 (각 NFT 고유) |
| 전송 함수 | `transfer(to, amount)` | `safeTransferFrom(from, to, tokenId)` |
| 메타데이터 | 없음 | `tokenURI(tokenId)` |
| 용도 | 화폐, 거버넌스 | 예술작품, 게임 아이템, 인증서 |

### NFT 메타데이터 구조

```json
{
  "name": "KNU NFT #0",
  "description": "경북대학교 블록체인 기술 강의 2026 — 수강 인증 NFT",
  "image": "ipfs://QmXxx.../image.png",
  "attributes": [
    { "trait_type": "Week", "value": "14" },
    { "trait_type": "Course", "value": "ICAB0203-001" }
  ]
}
```

### IPFS (InterPlanetary File System)

```
전통 웹:  https://server.com/image.png  ← 서버 다운 시 접근 불가
IPFS:     ipfs://QmXxx.../image.png     ← 콘텐츠 해시 기반, 분산 저장

CID (Content Identifier): 파일 내용의 해시값
→ 파일이 변경되면 CID가 달라짐 → 변조 불가능
```

---

## ▶ 실습 순서

### STEP 1: 교수님 제공 tokenURI 확인

수업 전 교수님이 공지하는 샘플 tokenURI를 사용합니다:

```
https://gateway.pinata.cloud/ipfs/[교수님 공지 CID]
```

> 📌 이 URL을 브라우저에서 열면 메타데이터 JSON을 확인할 수 있습니다.

---

### STEP 2: Remix에서 파일 생성 및 컴파일

1. https://remix.ethereum.org 접속
2. `contracts/KNUNFT.sol` 새 파일 생성
3. `week14/KNUNFT.sol` 내용 붙여넣기
4. Solidity `0.8.20` 으로 컴파일
5. ✅ 컴파일 성공 확인

---

### STEP 3: Sepolia 배포

1. Deploy & Run → Environment: `Injected Provider - MetaMask`
2. MetaMask → Sepolia 선택
3. Constructor: `_maxSupply = 0` (무제한) 또는 원하는 숫자
4. `Deploy` → MetaMask Confirm
5. 배포된 **컨트랙트 주소** 복사

---

### STEP 4: NFT 민팅

1. 배포된 컨트랙트 펼치기 → `mint` 함수
2. 입력:
   - `to`: 내 MetaMask 주소
   - `_tokenURI`: 교수님이 제공한 tokenURI
3. `transact` → MetaMask Confirm
4. 완료 후 터미널에서 `NFTMinted` 이벤트 확인

---

### STEP 5: 소유권 확인

```
ownerOf(0)     → 내 주소가 나오면 성공
tokenURI(0)    → 메타데이터 URL 확인
totalMinted()  → 1 (발행 수량)
nftInfo()      → 컨트랙트 전체 정보
tokensOfOwner(내주소) → [0] (내가 보유한 tokenId 목록)
```

---

### STEP 6: OpenSea Testnet에서 확인

```
https://testnets.opensea.io
```

1. 우측 상단 → 지갑 연결 (MetaMask)
2. 프로필 → `Collected` 탭
3. NFT가 표시될 때까지 대기 (수 분 소요)

> 💡 OpenSea에 바로 나타나지 않으면:
> https://testnets.opensea.io/assets/sepolia/[컨트랙트주소]/0
> 로 직접 접근하세요.

---

## ✅ 제출 기준

다음 내용을 LMS에 제출합니다.

- [ ] 스크린샷 1: `ownerOf(0)` → 내 주소 확인
- [ ] 스크린샷 2: OpenSea Testnet에서 내 NFT 확인
  - (또는 https://testnets.opensea.io/assets/sepolia/[주소]/0 스크린샷)

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

## 📌 교수 시연 내용 (학생 실습 불필요)

교수님이 수업 중 시연하는 IPFS 업로드 과정:

```
1. Pinata.cloud 로그인
2. 이미지 파일 업로드 → CID 획득
3. 메타데이터 JSON 작성 (image 필드에 IPFS CID 삽입)
4. JSON 파일 업로드 → tokenURI 확보
5. 확보된 tokenURI를 학생에게 공지
```

---

## 📝 생각해보기

1. NFT의 실제 이미지 파일은 블록체인에 저장되나요? 아니라면 어디에?
2. `tokenURI`가 가리키는 서버가 다운되면 NFT는 어떻게 될까요? IPFS는 이 문제를 어떻게 해결하나요?
3. ERC-1155는 ERC-20과 ERC-721을 어떻게 결합한 표준인가요?

---

*14주차 실습 가이드 v0.1 | ICAB0203-001*
