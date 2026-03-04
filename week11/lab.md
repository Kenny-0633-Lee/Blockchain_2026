# 11주차 실습 가이드 — Hardhat: 컴파일 · 테스트 · 배포

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.11 Tools & Languages

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 사용 도구 | Node.js + Hardhat |
| 실습 폴더 | `week11/` |
| 핵심 개념 | Hardhat · 컴파일 · 단위 테스트 · 배포 스크립트 |
| 제출물 | `npx hardhat test` 결과 스크린샷 → LMS |

---

## 🎯 학습 목표

- Hardhat 프로젝트 구조를 이해하고 설정한다
- `npx hardhat compile`로 Solidity 컨트랙트를 컴파일한다
- Mocha + Chai로 작성된 단위 테스트를 실행하고 결과를 해석한다
- `npx hardhat run scripts/deploy.js`로 로컬 배포를 수행한다

---

## 🔑 핵심 개념 요약

### Hardhat 프로젝트 구조

```
week11/
├── contracts/        ← Solidity 소스코드
│   └── SimpleStorage.sol
├── scripts/          ← 배포 스크립트
│   └── deploy.js
├── test/             ← 단위 테스트
│   └── SimpleStorage.test.js
├── hardhat.config.js ← Hardhat 설정
└── package.json
```

### Hardhat 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `npx hardhat compile` | Solidity → ABI + Bytecode 컴파일 |
| `npx hardhat test` | 테스트 실행 (Hardhat Network 자동 실행) |
| `npx hardhat run scripts/deploy.js` | 로컬 배포 |
| `npx hardhat console` | 인터랙티브 REPL |
| `npx hardhat node` | 로컬 테스트 노드 실행 (포트 8545) |

---

## ▶ 실습 순서

### STEP 1: Node.js 버전 확인

```bash
node --version   # v20.x.x 이상이어야 합니다
npm --version    # 10.x.x 이상
```

---

### STEP 2: 패키지 설치

```bash
cd week11
npm install
```

설치 완료 후 `node_modules/` 폴더가 생성됩니다.

---

### STEP 3: 컴파일

```bash
npx hardhat compile
```

**정상 출력 예시:**
```
Compiled 1 Solidity file successfully (evm target: paris).
```

`artifacts/contracts/SimpleStorage.sol/SimpleStorage.json` 파일이 생성됩니다.
이 파일이 ABI(Application Binary Interface)를 포함합니다.

---

### STEP 4: 단위 테스트 실행 ← **핵심**

```bash
npx hardhat test
```

**정상 출력 예시:**
```
  SimpleStorage
    배포 (Deployment)
      ✔ 배포자가 owner로 설정되어야 한다
      ✔ 초기 storedValue가 0이어야 한다
      ✔ 초기 updateCount가 0이어야 한다
    set()
      ✔ 값을 저장하고 get()으로 읽을 수 있어야 한다
      ✔ set() 호출 시 updateCount가 증가해야 한다
      ✔ 누구나 set()을 호출할 수 있어야 한다
      ✔ set() 호출 시 ValueChanged 이벤트가 발생해야 한다
      ✔ ValueChanged 이벤트에 oldValue와 newValue가 정확해야 한다
    reset()
      ✔ owner가 reset()을 호출하면 0이 되어야 한다
      ✔ owner가 아니면 reset()이 실패해야 한다 (Unauthorized)
    getInfo()
      ✔ owner, value, updateCount를 모두 반환해야 한다
    Gas 소비
      ✔ get()은 외부 트랜잭션 없이 호출 가능 (view 함수)
      ✔ set()은 Gas를 소비하는 트랜잭션이어야 한다

  13 passing (XXms)
```

---

### STEP 5: 배포 스크립트 실행

```bash
npx hardhat run scripts/deploy.js
```

**정상 출력 예시:**
```
========================================================
  SimpleStorage 컨트랙트 배포
========================================================

  배포자 주소  : 0xf39F...
  잔액         : 10000.0 ETH

  컨트랙트 컴파일 중...
  배포 중...

  ✅ 배포 완료!
  컨트랙트 주소: 0x5FbD...
  초기 저장값  : 42
  네트워크     : unknown (chainId: 31337)
```

---

### STEP 6: (선택) 직접 테스트 코드 추가

`test/SimpleStorage.test.js` 파일에 새 테스트를 추가해보세요:

```javascript
it("값 0도 저장할 수 있어야 한다", async function () {
    const { contract } = await loadFixture(deploySimpleStorageFixture);
    await contract.set(0n);
    expect(await contract.get()).to.equal(0n);
});
```

---

## ✅ 제출 기준

`npx hardhat test` 실행 결과에서 **모든 테스트가 passing**인 스크린샷 제출.

- [ ] `13 passing` (또는 그 이상) 확인
- [ ] 실패(failing) 항목 없음

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

## 🔴 트러블슈팅

| 증상 | 해결 |
|------|------|
| `npm install` 오류 | `node --version` v20 이상 확인 |
| `Cannot find module 'hardhat'` | `week11` 폴더 안에서 명령 실행 확인 |
| 컴파일 오류 | Solidity 버전이 `0.8.20`인지 확인 |
| 테스트 timeout | `hardhat.config.js`의 `timeout: 60000` 증가 |

---

*11주차 실습 가이드 v0.1 | ICAB0203-001*
