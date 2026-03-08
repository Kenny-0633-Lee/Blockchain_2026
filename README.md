# 🔗 블록체인 기술 — Blockchain Technology

**경북대학교 | DNA/ABB | ICAB0203-001 | 2026년 1학기**

---

## 📚 강의 허브 (Notion)

> 모든 강의 자료, 실습 가이드, 환경 설정, FAQ는 **Notion 허브**에서 확인하세요.

### 👉 [https://kenny-lee.notion.site/blockchain-knu2026](https://kenny-lee.notion.site/blockchain-knu2026)

> 이 저장소는 **실습 코드** 전용입니다.
> 강의노트·실습 가이드·제출 방법은 모두 Notion 허브를 참조하세요.

---

## 🚀 빠른 시작

### 사전 준비 (Week 2 환경 구축 완료 필수)

환경 설정이 되지 않은 경우 → [Notion 허브 > 환경 설정 가이드](https://kenny-lee.notion.site/blockchain-knu2026) 참조

### Python 실습 (3~6주차)

```powershell
# Windows PowerShell
git clone https://github.com/Kenny-0633-Lee/Blockchain_2026.git
cd Blockchain_2026
uv sync
uv run python week03/merkle_tree.py   # 예시: 3주차
```

```bash
# macOS / Linux
git clone https://github.com/Kenny-0633-Lee/Blockchain_2026.git
cd Blockchain_2026
uv sync
uv run python week03/merkle_tree.py
```

---

## 📅 주차별 안내 (W01 ~ W15)

> 각 주차 강의노트·실습 가이드는 **Notion 허브**에서 해당 주차 카드를 클릭하세요.
> 아래 표는 GitHub 폴더 구조와 실습 코드 안내입니다.

---

### Week 01 — Orientation & MetaMask

| 항목 | 내용                                                        |
| ---- | ----------------------------------------------------------- |
| 주제 | 강의 소개, 블록체인 개요, MetaMask 설치 및 Sepolia ETH 수령 |
| 실습 | MetaMask 설치 → Tally 폼 Connect Wallet → ETH 수령 확인     |
| 코드 | 없음 (GUI 실습)                                             |
| 과제 | MetaMask 잔액 + Etherscan 트랜잭션 스크린샷                 |

> 📖 [Notion 허브 > 1주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 02 — Blockchain 101 + 개발 환경 구축

| 항목 | 내용                                                               |
| ---- | ------------------------------------------------------------------ |
| 주제 | Ch.1 블록체인 기초, 분산 시스템, 합의 개요                         |
| 실습 | Git · uv · VS Code · Node.js 설치 + `blockchain_simulator.py` 실행 |
| 코드 | `week02/blockchain_simulator.py`                                   |
| 과제 | 5개 명령어 버전 출력 스크린샷 (`git`, `uv`, `code`, `node`, `npm`) |

```powershell
uv run python week02/blockchain_simulator.py
```

> 📖 [Notion 허브 > 2주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 03 — Decentralization & Merkle Tree

| 항목 | 내용                                                         |
| ---- | ------------------------------------------------------------ |
| 주제 | Ch.2 탈중앙화, 비잔틴 장군 문제, Merkle Tree 구조            |
| 실습 | `merkle_tree.py` — Merkle Root 계산, 변조 감지, Merkle Proof |
| 코드 | `week03/merkle_tree.py`                                      |
| 과제 | 실행 결과 스크린샷 (Merkle Root 출력 + 변조 감지 True)       |

```powershell
uv run python week03/merkle_tree.py
```

> 📖 [Notion 허브 > 3주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 04 — Cryptography Fundamentals I (Symmetric)

| 항목      | 내용                                                   |
| --------- | ------------------------------------------------------ |
| 주제      | Ch.3 대칭 암호학, SHA-256, AES, HMAC                   |
| 실습      | `sha256_aes.py` — Avalanche Effect 측정, AES 암·복호화 |
| 코드      | `week04/sha256_aes.py`                                 |
| 과제      | 실행 결과 스크린샷 (Avalanche 비율 + 암·복호화 결과)   |
| 추가 설치 | `uv add cryptography`                                  |

```powershell
uv add cryptography
uv run python week04/sha256_aes.py
```

> 📖 [Notion 허브 > 4주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 05 — Cryptography Fundamentals II (Asymmetric + Bitcoin Wallet)

| 항목 | 내용                                                       |
| ---- | ---------------------------------------------------------- |
| 주제 | Ch.4 비대칭 암호학, ECDSA, BIP-39, HD Wallet               |
| 실습 | `bip39_ecdsa_address.py` — 니모닉 생성 → Bitcoin 주소 도출 |
| 코드 | `week05/bip39_ecdsa_address.py`                            |
| 과제 | 실행 결과 스크린샷 (니모닉 → 주소 도출 결과)               |

```powershell
uv run python week05/bip39_ecdsa_address.py
```

> ⚠️ 실습용 니모닉은 실제 자산 보관 금지
> 📖 [Notion 허브 > 5주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 06 — Consensus Mechanisms (PoW)

| 항목 | 내용                                           |
| ---- | ---------------------------------------------- |
| 주제 | Ch.5 합의 메커니즘, PoW, PoS 비교, 난이도 조정 |
| 실습 | `pow_simulator.py` — 난이도별 채굴 시간 측정   |
| 코드 | `week06/pow_simulator.py`                      |
| 과제 | 실행 결과 스크린샷 (난이도별 채굴 시간 비교)   |

```powershell
uv run python week06/pow_simulator.py
```

> 📖 [Notion 허브 > 6주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 07 — Bitcoin Architecture (Electrum Testnet4)

| 항목      | 내용                                                 |
| --------- | ---------------------------------------------------- |
| 주제      | Ch.6 & 7 Bitcoin 아키텍처, UTXO 모델, P2PKH          |
| 실습      | Electrum Testnet4 — 지갑 생성, Faucet, 트랜잭션 전송 |
| 코드      | 없음 (GUI 실습)                                      |
| 과제      | Testnet4 주소 + 잔액 확인 스크린샷                   |
| 추가 설치 | Electrum (6주차 말미 안내)                           |

```powershell
# Windows: Electrum Testnet4 실행
.\electrum-*.exe --testnet
```

```bash
# macOS
open -a Electrum --args --testnet
```

> 📖 [Notion 허브 > 7주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 08 — 중간고사 🗒️

| 항목      | 내용              |
| --------- | ----------------- |
| 시험 범위 | 1~7주차 이론 전반 |
| 형식      | 필기시험          |
| 코드      | 없음              |

> 📖 [Notion 허브 > 시험 범위 공지](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 09 — Ethereum Architecture & EVM

| 항목 | 내용                                                          |
| ---- | ------------------------------------------------------------- |
| 주제 | Ch.9 Ethereum Account 모델, EVM, Gas 시스템                   |
| 실습 | MetaMask + Sepolia — 가스 설정, 트랜잭션 전송, Etherscan 확인 |
| 코드 | 없음 (GUI + Etherscan 실습)                                   |
| 과제 | Etherscan 트랜잭션 링크 (본인 주소 트랜잭션 1건)              |

> 📖 [Notion 허브 > 9주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 10 — Smart Contracts & Solidity I (Remix)

| 항목 | 내용                                                     |
| ---- | -------------------------------------------------------- |
| 주제 | Ch.8 & 11 스마트 컨트랙트 기초, Solidity 문법            |
| 실습 | Remix IDE — `SimpleStorage.sol` 작성·컴파일·Sepolia 배포 |
| 코드 | `week10/SimpleStorage.sol`                               |
| 과제 | 배포된 컨트랙트 주소 제출                                |

> 브라우저 기반 (설치 불필요): https://remix.ethereum.org
> 📖 [Notion 허브 > 10주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 11 — Smart Contracts & Solidity II (Hardhat)

| 항목 | 내용                                                     |
| ---- | -------------------------------------------------------- |
| 주제 | Ch.11 Hardhat 개발 환경, 테스트, Sepolia 배포 자동화     |
| 실습 | Hardhat init → 로컬 테스트 → Sepolia 배포 스크립트       |
| 코드 | `week11/contracts/`, `week11/scripts/`, `week11/test/`   |
| 과제 | `npx hardhat test` 통과 스크린샷 + Sepolia 컨트랙트 주소 |
| 주의 | `.env` 파일에 개인키 저장 — **절대 GitHub 커밋 금지**    |

```powershell
cd week11
npm install
npx hardhat test
npx hardhat run scripts/deploy.js --network sepolia
```

> 📖 [Notion 허브 > 11주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 12 — Web3 & DApps (ethers.js)

| 항목 | 내용                                                |
| ---- | --------------------------------------------------- |
| 주제 | Ch.12 Web3 아키텍처, ethers.js v6, Alchemy RPC 연동 |
| 실습 | ethers.js — 잔액 조회, 트랜잭션 전송, 컨트랙트 호출 |
| 코드 | `week12/scripts/`                                   |
| 과제 | 잔액 조회 또는 트랜잭션 전송 성공 스크린샷          |
| RPC  | Alchemy Sepolia (강의 허브 참조)                    |

```powershell
cd week12
npm install
node scripts/query_balance.js
```

> 📖 [Notion 허브 > 12주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 13 — Token Standards (ERC-20)

| 항목 | 내용                                                          |
| ---- | ------------------------------------------------------------- |
| 주제 | Ch.10 & 15 ERC-20 표준, OpenZeppelin, 토큰 발행               |
| 실습 | Remix — `KNUToken.sol` (KNUT) 작성·Sepolia 배포·MetaMask 추가 |
| 코드 | `week13/KNUToken.sol`                                         |
| 과제 | 배포된 KNUT 컨트랙트 주소 제출                                |

> 브라우저 기반: https://remix.ethereum.org
> 📖 [Notion 허브 > 13주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 14 — NFT (ERC-721) + Pinata

| 항목 | 내용                                                                                         |
| ---- | -------------------------------------------------------------------------------------------- |
| 주제 | Ch.10 & 15 ERC-721 표준, IPFS, Pinata 메타데이터                                             |
| 실습 | Pinata 이미지 업로드 → 메타데이터 생성 → KNUNFT 민팅 → Etherscan 확인 (또는 Rarible Testnet) |
| 코드 | `week14/KNUNFT.sol`                                                                          |
| 과제 | KNUNFT 컨트랙트 주소 + Etherscan tokenURI 확인 화면 (또는 Rarible Testnet 링크)              |

> 브라우저 기반: https://remix.ethereum.org / https://pinata.cloud
> 📖 [Notion 허브 > 14주차 강의자료](https://kenny-lee.notion.site/blockchain-knu2026)

---

### Week 15 — 기말고사 🗒️

| 항목      | 내용                                         |
| --------- | -------------------------------------------- |
| 시험 범위 | 9~14주차 이론 전반                           |
| 형식      | 필기시험 또는 텀프로젝트 발표 (학기 초 결정) |
| 코드      | 없음                                         |

> 📖 [Notion 허브 > 시험 범위 공지](https://kenny-lee.notion.site/blockchain-knu2026)

---

## 📦 Python 패키지 목록

| 패키지         | 용도                            | 주차   |
| -------------- | ------------------------------- | ------ |
| `cryptography` | AES 암호화, HMAC                | 4주차~ |
| `ecdsa`        | 타원곡선 서명 (secp256k1)       | 5주차  |
| `base58`       | Bitcoin 주소 Base58Check 인코딩 | 5주차  |
| `mnemonic`     | BIP-39 니모닉 생성              | 5주차  |
| `bip-utils`    | HD Wallet 파생 경로 (BIP-44)    | 5주차  |

> `uv sync` 한 번으로 모두 설치됩니다.

---

## 🔗 주요 링크

| 이름                           | 링크                                             |
| ------------------------------ | ------------------------------------------------ |
| 📝 **강의 허브 (Notion)**      | https://kenny-lee.notion.site/blockchain-knu2026 |
| Sepolia Etherscan              | https://sepolia.etherscan.io                     |
| Remix IDE                      | https://remix.ethereum.org                       |
| Bitcoin Testnet4 Mempool       | https://mempool.space/testnet4                   |
| Rarible Testnet (OpenSea 대체) | https://testnet.rarible.com                      |
| Sepolia Faucet (Alchemy)       | https://www.alchemy.com/faucets/ethereum-sepolia |
| Bitcoin Testnet4 Faucet        | https://mempool.space/testnet4/faucet            |
| Electrum                       | https://electrum.org/#download                   |
| Hardhat 문서                   | https://hardhat.org/docs                         |
| ethers.js v6                   | https://docs.ethers.org/v6                       |

---

## 👨‍🏫 교수 정보

| 항목                  | 값                                           |
| --------------------- | -------------------------------------------- |
| 이메일                | infosec@knu.ac.kr                            |
| Sepolia 주소          | `0x21d9795E987694a2a8E1ad7FF2250c953D166896` |
| Bitcoin Testnet4 주소 | `tb1qwqnjsfm5l4mf3m5n28vpkjd0hvqep5acx8nx97` |

---

> 📌 `instructor/` 폴더는 교수 전용 private 브랜치에서 관리됩니다.

_최종 업데이트: 2026-03-07 | 코드셋 버전: v0.93 | ICAB0203-001_
