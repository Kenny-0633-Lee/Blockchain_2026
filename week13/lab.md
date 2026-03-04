# 13주차 실습 가이드 — KNU Token (KNUT) ERC-20 발행

> **경북대학교 블록체인 기술 | ICAB0203-001 | 2026년 1학기**
> 교재: Mastering Blockchain 4th Ed. — Ch.10 & Ch.15 Tokenization

---

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| 실습 도구 | Remix IDE + MetaMask (Sepolia) |
| 실습 코드 | `week13/KNUToken.sol` |
| 핵심 개념 | ERC-20 · OpenZeppelin · decimals · approve/transferFrom |
| 제출물 | 교수님 지갑으로 KNUT 전송 TxHash → LMS |

---

## 🎯 학습 목표

- ERC-20 표준의 6개 필수 함수와 2개 이벤트를 이해한다
- OpenZeppelin ERC20을 상속하여 토큰을 발행한다
- `decimals`와 `10^18` 단위 변환을 이해한다
- `approve` / `transferFrom` 패턴(DeFi의 핵심)을 이해한다
- MetaMask에 커스텀 토큰을 추가하고 잔액을 확인한다

---

## 🔑 핵심 개념 요약

### ERC-20 필수 인터페이스

```solidity
interface IERC20 {
    // 필수 함수 (6개)
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);

    // 필수 이벤트 (2개)
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

### Decimals와 단위 변환

```
사람이 보는 값: 1 KNUT
실제 저장 값:   1,000,000,000,000,000,000 (= 1 × 10^18 = 1e18)

왜? 소수점 이하 18자리까지 표현하기 위해
Solidity는 소수점 없음 → 정수로 18자리 패딩

1 ETH   = 1,000,000,000,000,000,000 Wei  (10^18)
1 KNUT  = 1,000,000,000,000,000,000 (10^18) → decimals() = 18
```

### approve / transferFrom (DeFi의 핵심)

```
일반 transfer:  Alice → Bob 직접 전송 (서명 필요)

DeFi 패턴:
1. Alice가 DEX에게 approve(dex, 100 KNUT) → DEX가 내 100 KNUT 사용 허가
2. DEX가 exchangeToken() 호출 → transferFrom(Alice, pool, 100 KNUT)
3. 실제 토큰 이동은 DEX가 실행
```

---

## ▶ 실습 순서

### STEP 1: Remix에서 파일 생성

1. https://remix.ethereum.org 접속
2. `contracts/` → 새 파일 → `KNUToken.sol`
3. `week13/KNUToken.sol` 내용 붙여넣기

---

### STEP 2: 컴파일

1. Solidity Compiler 탭 → `0.8.20`
2. `Compile KNUToken.sol`
3. ✅ 초록 체크마크 확인

---

### STEP 3: Sepolia 배포

1. Deploy & Run → Environment: `Injected Provider - MetaMask`
2. MetaMask → Sepolia Testnet 선택
3. Constructor: `initialSupply = 1000000`
4. `Deploy` → MetaMask Confirm (Gas 소모)
5. 배포된 컨트랙트 주소 복사 (제출용)

---

### STEP 4: 함수 호출

**정보 조회:**
```
tokenInfo()  → name, symbol, decimals, totalSupply, owner 확인
balanceInTokens(내주소) → 1,000,000 KNUT 확인
totalSupply()           → 1000000000000000000000000 (10^24) 확인
```

**토큰 전송:**
```
transfer(교수님주소, 전송량)
  수신 주소: 0x21d9795E987694a2a8E1ad7FF2250c953D166896
  금액: 1000000000000000000 (= 1 KNUT × 10^18)
```

> 💡 Remix에서 amount 입력 시 반드시 18자리 0을 붙여야 합니다.
> `1 KNUT = 1000000000000000000`

**추가 발행 (owner만):**
```
mint(내주소, 1000)  → 1,000 KNUT 추가 발행
```

**approve 실습:**
```
1. approve(다른주소, 500000000000000000000)  → 500 KNUT 허가
2. allowance(내주소, 다른주소) → 500 KNUT 확인
```

---

### STEP 5: MetaMask에 KNUT 토큰 추가

1. MetaMask → `Import tokens`
2. `Custom token` 탭
3. Token contract address: 배포된 컨트랙트 주소 입력
4. 자동으로 Symbol(KNUT), Decimals(18) 채워짐
5. `Add custom token` → `Import tokens`
6. MetaMask에서 KNUT 잔액 확인

---

### STEP 6: Sepolia Etherscan에서 토큰 확인

```
https://sepolia.etherscan.io/token/[컨트랙트주소]
```

- `Holders` 탭: 토큰 보유자 목록
- `Transfers` 탭: 전송 내역

---

## ✅ 제출 기준

다음 내용을 LMS에 제출합니다.

- [ ] 스크린샷: `tokenInfo()` 결과 (name, symbol, totalSupply 확인)
- [ ] 스크린샷: MetaMask에서 KNUT 토큰 잔액 확인
- [ ] TxHash: 교수님 주소로 KNUT 전송 트랜잭션 해시

```
교수님 Sepolia 주소: 0x21d9795E987694a2a8E1ad7FF2250c953D166896
```

**제출 기한**: 해당 주차 수업일로부터 7일 이내

---

## 📝 생각해보기

1. ERC-20 `approve/transferFrom`이 없다면 DEX(탈중앙화 거래소)는 어떻게 동작해야 할까요?
2. `totalSupply`가 무한히 증가할 수 있는 토큰의 문제점은 무엇인가요?
3. OpenZeppelin을 사용하는 이유가 단순한 편의성 때문만일까요?

---

*13주차 실습 가이드 v0.1 | ICAB0203-001*
