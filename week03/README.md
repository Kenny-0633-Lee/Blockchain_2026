# 3주차 실습 가이드 — Merkle Tree 구현

**경북대학교 블록체인 기술 | ICAB0203-001**

---

## 학습 목표

- Merkle Tree 구조와 Hash Pointer 이해
- SHA-256 기반 트리 구성 원리 체험
- Merkle Proof(포함 증명)로 특정 TX가 블록에 포함됐음을 O(log n)으로 검증
- Bitcoin SPV(Simplified Payment Verification)의 기반 원리 이해

---

## 사전 준비

```powershell
cd Blockchain_2026
uv sync   # 패키지 설치 확인
```

별도 외부 패키지 없음 — Python 표준 라이브러리 `hashlib`만 사용합니다.

---

## 실행

```powershell
uv run python week03/merkle_tree.py
```

---

## 시나리오 설명

| 시나리오 | 내용 |
|----------|------|
| **1. 기본 구성** | 4개 TX → 리프 해시 → 레벨별 트리 구성 → Merkle Root 출력 |
| **2. Merkle Proof** | TX[1]의 포함 증명 생성 → 검증 → 변조 TX 검증 시도 |
| **3. 홀수 처리** | 3개 TX → 마지막 노드 복제 (Bitcoin 방식) |
| **4. 변조 감지** | TX 1개만 수정해도 Root가 완전히 달라짐 확인 |

---

## 핵심 코드 구조

```
MerkleTree 클래스
├── __init__(transactions)    # 트리 생성
├── _build()                  # 레벨별 해시 계산 → Root 반환
├── get_proof(tx_index)       # Merkle Proof 경로 추출
├── verify_proof(tx, proof)   # Root와 비교하여 포함 여부 검증
└── display()                 # 트리 시각적 출력
```

---

## 예상 출력 (일부)

```
📦 시나리오 1: 기본 Merkle Tree 구성

  [0] Alice → Bob: 1.5 BTC   → a3f8b4...
  [1] Bob → Carol: 0.3 BTC   → 2d9e1f...
  [2] Carol → Dave: 2.0 BTC  → 7c4a82...
  [3] Dave → Alice: 0.7 BTC  → f1b3d9...

🌳 Merkle Root:
  9e3f2d1a8b...
```

---

## 토의 질문

1. Merkle Root만 알면 트랜잭션 전체 없이도 특정 TX의 포함 여부를 왜 검증할 수 있나요?
2. TX가 1,000개인 블록에서 Merkle Proof 경로의 길이는 몇 단계인가요? (힌트: log₂)
3. Bitcoin SPV 노드가 Merkle Proof를 사용하는 이유는 무엇인가요?

---

## 제출

터미널 출력 **전체 스크린샷 1장** → LMS 3주차 제출함

---

*v0.1 | 2026-03-04*
