# 05. 모바일 신분증(DID/VC) 개념 시뮬레이션

**메시지:** 블록체인은 코인이 아니라 *위조할 수 없는 공개키 명부(Trust Anchor)* 로도 쓰인다.
체인에는 `DID → 공개키`와 폐지 기록만 있고, 개인정보는 폰(지갑)에만 있다.

## 실행

```bash
uv run python special_topic_2026/05_did_mobile_id/did_demo.py          # Enter 로 진행
uv run python special_topic_2026/05_did_mobile_id/did_demo.py --auto   # 한 번에
```
macOS 터미널 / Windows PowerShell·Git Bash 공통. 의존성: `cryptography`.

## 단계

0~2 허가형 원장(노드 4개, quorum 3) 생성 · 발급기관 DID 등록 · 속성별 salt+해시 커밋에 서명 →
3 정상 검증 → 4-A 가짜 발급기관 / 4-B 값 변조 / 4-C 재사용(replay) / 4-D 원장 위·변조 / 4-E 폐지 →
5 선택적 공개(편의점·렌터카·은행에 서로 다른 속성)

## 참고 (사실 확인 범위)

- 모바일 운전면허증: 경찰청 발급, 행안부·한국조폐공사 발주, LG CNS 주관, 라온시큐어 OmniOne DID 플랫폼 ([블록미디어](https://www.blockmedia.co.kr/archives/183123)).
- OmniOne OpenDID 는 [GitHub OmniOneID](https://github.com/OmniOneID) 에 공개(Apache-2.0 로 표기된 저장소 다수). 설계 개요: [OpenDID 슬라이드](https://openchain-project.github.io/OpenChain-KWG/slides/OpenDID_20250325.pdf).
- 실제 운영 체인의 종류는 공개 자료로 확정하지 못했습니다. 슬라이드에는 "허가형 블록체인"까지만 씁니다.

## 한계

- 합의는 단순화(정직한 노드 전원이 같은 블록에 서명). 실제 BFT 합의는 구현하지 않았습니다.
- `adult_19` 는 발급기관이 미리 계산해 서명한 속성입니다. 생년월일을 숨긴 채 나이를 증명하는 범위 증명은 ZK 가 필요해 이번 특강에서 제외했습니다.
- 선택적 공개는 SD-JWT 와 유사한 salt+해시 방식의 개념 시연이며, 실제 한국 신분증의 방식과 같다고 확인된 것이 아닙니다.
