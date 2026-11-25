저장소 special_topic_2026/05_did_mobile_id/ 폴더에 이 폴더의 did_viz.html 과 did_demo.py 를 덮어 복사하세요.
(did_demo.py 는 기존 코드에 --web 옵션만 추가했습니다. 시나리오·검증 로직은 그대로입니다.)

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/05_did_mobile_id/did_demo.py --web

special_topic_2026/README.md 수정 3곳
  1) 표의 05 행 맨 끝 시간 칸:  1초  ->  1초 (+ `--web`)
  2) `--web` 옵션 설명의 (`01`, `06`, `07`, `A1`) 에 `05` 추가
  3) 브라우저 시각화 표에 한 줄 추가:
     | `05_did_mobile_id/did_viz.html` | 허가형 원장·발급기관·지갑·검증자 4개 화면, 단계 0~5와 공격 5종(4-A~4-E), 검증 7항목 순차 표시 |
