# 특강 2026-11-25 — 블록체인 (경북대, 암호공학 이론 수강생 대상, 90분)

슬라이드(PPTX)가 메인이고, 실습이 필요한 대목에서 **Notion 시나리오 페이지**로 전환해 아래 코드를 실행합니다.
(Notion: 대학 강의 DB › 블록체인_2026 뷰 › "11/25 특강" 페이지)

## 시연 목록

| 폴더 | 파일 | 보여주는 것 | 의존성 | 시간 |
|---|---|---|---|---|
| `01_merkle_tamper` | `merkle_tamper.py` | 변조가 루트까지 번지는 모습, 포함 증명 log₂n | 표준 라이브러리 | 약 2분 (+ `--web`) |
| `02_pow_mining` | `pow_demo.py` | 난이도별 채굴(×16), 과거 블록 변조 비용 | 표준 라이브러리 | 약 1분 (Enter 진행) |
| `03_bip39_wallet` | `bip39_demo.py` | 12단어 → 시드 → 키 → BTC/ETH 주소 | `bip-utils` | 1초 |
| `04_sre_nft_mint` | (README만) | Scaffold-ETH 2 로 NFT 민팅 | Node ≥ 20.18.3, Yarn | 사전 리허설 필수 |
| `05_did_mobile_id` | `did_demo.py` | 모바일 신분증(DID/VC) 개념: 허가형 원장, 공격 5종, 선택적 공개 | `cryptography` | 1초 |
| `06_ai_model_provenance` | `model_provenance.py` | AI 모델 가중치 Merkle root 서명, 1비트 변조 적발, 이력 해시 체인 | `cryptography` | 약 3분 (+ `--web`) |
| `07_ai_opml_verification` | `opml_demo.py` | opML 이분 탐색(10회 비교로 1,024단계 중 조작 적발), 불시 검사 손익분기 | 표준 라이브러리 | 약 3분 (+ `--web`) |

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

## 진행 방식 (모든 터미널 시연 공통, `_common/demo_kit.py`)

각 시연은 **중간값을 단계별로 출력**하고, 단계 사이에서 멈춥니다.

| 입력 | 동작 |
|---|---|
| Enter | 다음 단계 |
| `a` + Enter | 남은 단계를 멈춤 없이 끝까지 |
| `q` + Enter | 종료 |

| 옵션 | 동작 |
|---|---|
| `--auto` | 멈춤 없이 실행 (리허설·점검용) |
| `--fast` | 애니메이션 지연 없이 |
| `--web` | 브라우저 시각화 열기 (`01`, `06`, `07`) |

출력을 파이프/파일로 보내면 자동으로 `--auto --fast` 가 적용됩니다.

## 브라우저 시각화 (`--web`, 인터넷 불필요·단일 HTML)

| 파일 | 내용 |
|---|---|
| `01_merkle_tamper/merkle_viz.html` | Merkle 트리 단계별 구성, 클릭한 리프 변조 → 붉은 경로, 증명 경로 |
| `06_ai_model_provenance/provenance_viz.html` | 모델 16조각 + 트리, 1비트 변조, 4번 비교로 조각 찾기, 증명 경로 |
| `07_ai_opml_verification/opml_viz.html` | A) 1,024단계 격자 이분 탐색 B) 불시 검사 손익 슬라이더·10,000건 시뮬레이션 |

키: Space/Enter/→ 다음, ← 이전, R 처음부터. 파일을 더블클릭해도 열립니다.

## 주의

- 모든 코드는 **교육용 개념 시뮬레이션**입니다. 특히 `05`는 실제 모바일 신분증(OmniOne OpenDID 등)의 내부 구현과 같다고 주장하지 않으며, DID 이름은 예시입니다.
- `06`의 '모델 가중치'는 시연용 난수 바이트입니다.
- `07`은 opML/Proof of Sampling의 핵심 아이디어를 단순화한 것입니다.
- `03`이 만드는 니모닉에 실제 자산을 넣지 마세요.
