# 특강 2026-11-25 — 블록체인 (경북대, 암호공학 이론 수강생 대상, 90분)

슬라이드(PPTX)가 메인이고, 실습이 필요한 대목에서 **Notion 시나리오 페이지**로 전환해 아래 코드를 실행합니다.
(Notion: 대학 강의 DB › 블록체인_2026 뷰 › "11/25 특강" 페이지)

## 시연 목록

| 폴더 | 파일 | 보여주는 것 | 의존성 | 시간 |
|---|---|---|---|---|
| `01_merkle_tamper` | `merkle_tamper.py` | 변조가 루트까지 번지는 모습, 포함 증명 log₂n | 표준 라이브러리 | 1초 |
| `02_pow_mining` | `pow_demo.py` | 난이도별 채굴(×16), 과거 블록 변조 비용 | 표준 라이브러리 | 약 8초 |
| `03_bip39_wallet` | `bip39_demo.py` | 12단어 → 시드 → 키 → BTC/ETH 주소 | `bip-utils` | 1초 |
| `04_sre_nft_mint` | (README만) | Scaffold-ETH 2 로 NFT 민팅 | Node ≥ 20.18.3, Yarn | 사전 리허설 필수 |
| `05_did_mobile_id` | `did_demo.py` | 모바일 신분증(DID/VC) 개념: 허가형 원장, 공격 5종, 선택적 공개 | `cryptography` | 1초 |
| `06_ai_model_provenance` | `model_provenance.py` | AI 모델 가중치 Merkle root 서명, 1비트 변조 적발, 이력 해시 체인 | `cryptography` | 1초 |
| `07_ai_opml_verification` | `opml_demo.py` | opML 이분 탐색(10회 비교로 1,024단계 중 조작 적발), 불시 검사 손익분기 | 표준 라이브러리 | 1초 |

## 실행 (저장소 루트에서)

```bash
# macOS / Linux
uv sync
uv run python special_topic_2026/01_merkle_tamper/merkle_tamper.py
```

```powershell
# Windows PowerShell 또는 Git Bash (명령 동일)
uv sync
uv run python special_topic_2026/01_merkle_tamper/merkle_tamper.py
```

`uv` 가 없으면 `pip install cryptography bip-utils` 후 `python ...`(Windows 에서 안 되면 `py ...`)로 실행해도 됩니다.
`05_did_mobile_id/did_demo.py` 는 Enter 로 단계가 넘어가며, `--auto` 를 붙이면 멈춤 없이 실행됩니다.

## 주의

- 모든 코드는 **교육용 개념 시뮬레이션**입니다. 특히 `05`는 실제 모바일 신분증(OmniOne OpenDID 등)의 내부 구현과 같다고 주장하지 않으며, DID 이름은 예시입니다.
- `06`의 '모델 가중치'는 시연용 난수 바이트입니다.
- `07`은 opML/Proof of Sampling의 핵심 아이디어를 단순화한 것입니다.
- `03`이 만드는 니모닉에 실제 자산을 넣지 마세요.
