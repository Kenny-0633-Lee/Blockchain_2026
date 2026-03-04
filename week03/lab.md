# 3주차 실습 가이드 — Merkle Tree 구현

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.2 Decentralization

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 실습 코드 | `week03/merkle_tree.py` |
| 핵심 개념 | Merkle Tree · Merkle Root · Merkle Proof |
| 제출물 | 실행 결과 스크린샷 → LMS 업로드 |

---

## 🎯 학습 목표

- SHA-256 이중 해시를 이용하여 Merkle Tree를 직접 구성한다
- 트랜잭션 목록 → Merkle Root 계산 과정을 단계별로 이해한다
- Merkle Proof가 전체 트랜잭션 없이 포함 여부를 증명하는 원리를 이해한다
- 트랜잭션 1개 변조가 Merkle Root를 완전히 바꿈을 확인한다

---

## 🔑 핵심 개념 요약

### Merkle Tree란?

```
         Merkle Root (블록 헤더에 저장)
              /\
             /  \
           H01  H23
           /\    /\
          /  \  /  \
        H0   H1 H2  H3
        |    |  |   |
       TX0  TX1 TX2 TX3   ← 트랜잭션 목록
```

- **리프 노드**: 각 트랜잭션을 SHA-256 이중 해시한 값
- **부모 노드**: 두 자식 해시를 결합하여 다시 해시
- **Merkle Root**: 최상위 해시. 블록 헤더의 `merkle_root` 필드에 저장

### 왜 Merkle Tree가 필요한가?

| 문제 | Merkle Tree 해결책 |
|------|-------------------|
| 블록에 수천 개의 TX 존재 | Root 하나로 전체 TX 요약 |
| TX 변조 여부 확인 | Root가 달라지므로 즉시 감지 |
| 경량 클라이언트(SPV) | 전체 TX 없이 Proof만으로 검증 |

### Merkle Proof (SPV 검증)

전체 트랜잭션 목록 없이 **특정 TX가 블록에 포함됐는지** 증명:

```
증명 대상: TX[1]
필요한 것: TX[1] 해시 + 형제 해시 목록 + Merkle Root
과정: H1 + H0 → H01 + H23 → Root (재계산 후 일치 확인)
```

---

## ▶ 실행 방법

```bash
# 저장소 루트에서 실행
uv run python week03/merkle_tree.py
```

---

## 📊 예상 출력

```
==============================================================
  3주차 실습: Merkle Tree 구현
==============================================================

[PART 1] 4개 트랜잭션으로 Merkle Tree 구성
--------------------------------------------------------------
  TX[0]: Alice → Bob : 0.5 BTC
  TX[1]: Bob → Carol : 0.3 BTC
  TX[2]: Carol → Dave : 0.1 BTC
  TX[3]: Dave → Alice : 0.05 BTC

  [Merkle Tree 구조 — 아래: 리프, 위: 루트]
  루트  : xxxxxxxx…
  레벨1 : xxxxxxxx…  xxxxxxxx…
  레벨0 : xxxxxxxx…  xxxxxxxx…  xxxxxxxx…  xxxxxxxx…

  ✅ Merkle Root: [64자리 16진수]

...

[PART 3] Merkle Proof — TX[1] 포함 여부 증명
  검증 결과: ✅ 유효 — 트랜잭션이 블록에 포함됨

[PART 4] 변조된 트랜잭션으로 Proof 검증 실패 확인
  동일 Proof로 검증: ❌ 실패 — 변조 감지됨

[PART 5] 트랜잭션 하나 변조 → Merkle Root 변화 확인
  루트 일치 여부: ❌ 다름 — 변조 감지 성공
```

---

## 🔍 코드 이해 포인트

### 1. `sha256d()` — 이중 해시

```python
def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
```

Bitcoin은 단일 SHA-256 대신 **이중 SHA-256**을 사용합니다. 길이 확장 공격(Length Extension Attack)에 대한 추가 방어입니다.

### 2. 홀수 처리

```python
if len(current) % 2 == 1:
    current.append(current[-1])   # 마지막 노드 복제
```

트랜잭션이 홀수개이면 마지막 트랜잭션을 복제하여 짝수를 맞춥니다. Bitcoin도 동일 방식을 사용합니다.

### 3. Merkle Proof 방향

```python
if idx % 2 == 0:         # 현재가 왼쪽
    proof.append(("right", sibling))
else:                    # 현재가 오른쪽
    proof.append(("left", sibling))
```

형제 노드의 **방향**을 함께 저장해야 부모 해시 재계산 시 순서를 맞출 수 있습니다.

---

## 📝 생각해보기 (토론 질문)

1. Merkle Tree가 없다면 SPV 클라이언트는 TX 포함 여부를 어떻게 검증해야 할까요?
2. 4개의 TX 중 TX[0]만 변조했을 때 어떤 해시값들이 바뀔까요? (직접 추적해보세요)
3. Bitcoin 블록에는 수천 개의 TX가 있습니다. Merkle Proof의 깊이는 몇 단계일까요?

---

## ✅ 제출 기준

다음이 모두 보이는 터미널 스크린샷을 LMS에 제출합니다.

- [ ] PART 1: Merkle Root 해시값 (64자리)
- [ ] PART 3: `✅ 유효` 메시지
- [ ] PART 4: `❌ 실패 — 변조 감지됨` 메시지
- [ ] PART 5: `❌ 다름 — 변조 감지 성공` 메시지

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

*3주차 실습 가이드 v0.1 | ICAB0203-001*
