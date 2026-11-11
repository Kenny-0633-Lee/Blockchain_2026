# 04. Scaffold-ETH 2 (SRE)로 NFT 민팅

> ⚠️ 이 폴더는 **교수 시연용 시나리오 메모**입니다. 이 문서의 명령은 특강 전 **본인 PC에서 1회 리허설**해 확인하세요.
> (저장소 작성 환경에서는 Node 프로젝트를 실행해 보지 못했습니다.)

## 사전 준비 (macOS / Windows 공통)

- Node.js **20.18.3 이상**, Yarn, Git. (`node -v`, `yarn -v` 로 확인)
- Windows 는 **PowerShell 또는 Git Bash** 에서 실행. 경로에 한글/공백이 없는 폴더 권장.
- 강의실 전 리허설용으로 90초 화면 녹화를 예비로 만들어 둡니다.

## 흐름 (터미널 3개)

```bash
# 터미널 0 (최초 1회): 프로젝트 생성
npx create-eth@2.0.23 -e challenge-tokenization challenge-tokenization
cd challenge-tokenization

# 터미널 1: 로컬 체인
yarn chain

# 터미널 2: 컨트랙트 배포
yarn deploy

# 터미널 3: 프런트엔드
yarn start        # http://localhost:3000
```

## 시연 순서

1. 브라우저에서 앱 열기 → burner wallet 주소 확인 (자동 생성, 개인키가 브라우저에 있음)
2. NFT 민팅 → 트랜잭션이 로컬 체인에 들어가는 것을 `yarn chain` 터미널에서 확인
3. *Debug Contracts* 탭에서 `ownerOf(tokenId)` 호출 → 내 주소가 소유자
4. 시크릿(비공개) 창으로 같은 앱 열기 → 다른 burner 주소 → 토큰 전송 → 소유자 변경 확인

## 설명 포인트

- NFT = ERC-721 컨트랙트 안의 `tokenId → owner` 매핑. "파일"이 아니라 "소유 기록".
- `tokenURI` 가 가리키는 메타데이터/이미지는 보통 체인 밖(IPFS 등)에 있고, 체인에는 링크(해시)만 있음.
- 모든 상태 변화는 서명된 트랜잭션 → 3~5주차의 ECDSA 가 그대로 쓰임.

## 실패 대응

- 포트 충돌(3000/8545): 이전 프로세스 종료 후 재실행
- 설치가 느림/실패: 예비 녹화 영상으로 대체
- `yarn` 이 없으면: `corepack enable` 후 재시도 (Node 에 포함된 corepack 사용)
