# 🔗 블록체인 기술 — Blockchain Technology

**경북대학교 | ICAB0203-001 | 2026년 1학기**
**코드셋 버전: v0.1**

---

## 📁 저장소 구조

```
Blockchain_2026/
├── week01/   1주차 — MetaMask + Sepolia ETH 배포 (교수용 스크립트)
├── week02/   2주차 — 개발 환경 구축 가이드
├── week03/   3주차 — Merkle Tree 구현 (Python)
├── week04/   4주차 — SHA-256 Avalanche Effect (Python)
├── week05/   5주차 — BIP-39 + ECDSA + Bitcoin 주소 도출 (Python)
├── week06/   6주차 — PoW 채굴 시뮬레이터 (Python)
├── week07/   7주차 — Electrum Testnet 실습 가이드
├── week09/   9주차 — Sepolia 가스 시스템 실습 가이드
├── week10/   10주차 — SimpleStorage.sol (Remix)
├── week11/   11주차 — Hardhat 로컬 개발 환경
├── week12/   12주차 — ethers.js + DApp 연동
├── week13/   13주차 — KNU Token ERC-20
└── week14/   14주차 — KNU NFT ERC-721
```

---

## 🚀 빠른 시작 (Python 실습 — 3~6주차)

```powershell
# 1. 저장소 클론
git clone https://github.com/Kenny-0633-Lee/Blockchain_2026.git
cd Blockchain_2026

# 2. uv로 가상환경 생성 및 패키지 설치
uv sync

# 3. 실습 코드 실행 예시 (3주차)
uv run python week03/merkle_tree.py
```

---

## 📦 Python 패키지 목록

| 패키지 | 용도 | 주차 |
|--------|------|------|
| `cryptography` | 암호화 기본 라이브러리 | 4주차 이후 |
| `ecdsa` | 타원곡선 서명 | 5주차 |
| `base58` | Bitcoin 주소 인코딩 | 5주차 |
| `mnemonic` | BIP-39 니모닉 생성 | 5주차 |
| `bip-utils` | HD Wallet 파생 경로 | 5주차 |

---

## 🔗 주요 링크

| 링크 | 주소 |
|------|------|
| 강의 노트 (Notion) | 수업 중 공유 |
| Sepolia Etherscan | https://sepolia.etherscan.io |
| Remix IDE | https://remix.ethereum.org |
| Bitcoin Testnet4 Mempool | https://mempool.space/testnet4 |
| OpenSea Testnet | https://testnets.opensea.io |

---

## 👨‍🏫 교수 정보

- **Sepolia 주소:** `0x21d9795E987694a2a8E1ad7FF2250c953D166896`
- **Bitcoin Testnet4 주소:** `tb1qwqnjsfm5l4mf3m5n28vpkjd0hvqep5acx8nx97`

---

*최종 업데이트: 2026-03-04 | v0.1*
