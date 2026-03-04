"""
week01/2_1_convert.py   [기존 Set — STEP 1/2]
==============================================
Tally CSV → students.json 변환 (교수용)

역할:
  - Tally 폼에서 내려받은 한글 헤더 CSV를
    2_2_distribute.py 가 읽을 수 있는 JSON 으로 변환
  - 지갑 주소 유효성 검사 (0x + 42자리 + hex 확인)
  - 중복 제출 주소 감지 및 경고   ← v0.2 추가

워크플로우:
  Tally CSV 수출
    → uv run python week01/2_1_convert.py
    → 00_Admin_Only/students.json 생성
    → uv run python week01/2_2_distribute.py --dry-run   # 확인
    → uv run python week01/2_2_distribute.py             # 실제 배포

CSV 예상 헤더 (Tally 설정에 맞게 수정):
  이름, 지갑주소(메타마스크)

출력 JSON 형식:
  [
    {"name": "홍길동", "wallet": "0x...", "status": "pending",
     "amount_eth": 0.1, "tx_hash": null},
    ...
  ]

⚠️  이 스크립트는 교수님만 실행합니다.
"""

import csv
import json
from collections import Counter
from pathlib import Path

# ── 설정 ─────────────────────────────────────────────────────
AMOUNT_ETH   = 0.1
CSV_ENCODING = "utf-8-sig"   # Tally CSV: BOM 포함 UTF-8

# Tally CSV 헤더 이름 (실제 폼 컬럼명에 맞게 수정)
HEADER_NAME   = "이름"
HEADER_WALLET = "지갑주소(메타마스크)"


def _is_valid_address(address: str) -> bool:
    """0x 접두사 + 40자리 hex 검사"""
    if not (address.startswith("0x") and len(address) == 42):
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def convert_csv_to_json(
    input_file:  str = "students_raw.csv",
    output_file: str = "students.json",
) -> None:
    """
    Tally CSV → students.json 변환

    v0.2 개선 내역:
      - 중복 지갑 주소 감지 및 경고
      - hex 유효성 2단계 검사 (길이 + int 파싱)
      - tx_hash 필드 초기화 (2_2_distribute.py 호환)
      - 행 번호 포함 경고 메시지
    """
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    csv_path  = base_path / input_file
    json_path = base_path / output_file

    if not csv_path.exists():
        print(f"[Error] CSV 파일 없음: {csv_path}")
        print("        Tally → 응답 내보내기 → CSV → 00_Admin_Only/ 에 저장")
        return

    student_list  = []
    invalid_list  = []
    address_count = Counter()   # 중복 감지용

    try:
        with open(csv_path, mode="r", encoding=CSV_ENCODING) as f:
            reader = csv.DictReader(f)

            if reader.fieldnames:
                print(f"[Info] CSV 헤더 확인: {list(reader.fieldnames)}")

            for row_num, row in enumerate(reader, start=2):
                name    = row.get(HEADER_NAME,   "").strip()
                address = row.get(HEADER_WALLET, "").strip()

                if not name and not address:   # 빈 행 무시
                    continue

                address_count[address] += 1

                if _is_valid_address(address):
                    student_list.append({
                        "name":       name,
                        "wallet":     address,
                        "status":     "pending",
                        "amount_eth": AMOUNT_ETH,
                        "tx_hash":    None,      # 2_2_distribute.py 호환
                    })
                else:
                    invalid_list.append((row_num, name, address))
                    print(f"[Warning] 유효하지 않은 주소 | 행 {row_num} | {name} | '{address}'")

    except Exception as e:
        print(f"[Critical Error] CSV 읽기 실패: {e}")
        return

    # ── 중복 주소 감지 (v0.2 추가) ──────────────────────────
    duplicates = {
        addr: cnt for addr, cnt in address_count.items()
        if cnt > 1 and addr
    }
    if duplicates:
        print(f"\n[Warning] 중복 지갑 주소 발견 ({len(duplicates)}건):")
        for addr, cnt in duplicates.items():
            names = [s["name"] for s in student_list if s["wallet"] == addr]
            print(f"  {addr[:20]}...  ({cnt}회 제출)  → {names}")
        print("  → JSON 에 모두 포함됩니다. 배포 전 수동 확인 권장.\n")

    # ── JSON 저장 ────────────────────────────────────────────
    base_path.mkdir(parents=True, exist_ok=True)
    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(student_list, f, indent=4, ensure_ascii=False)

    # ── 요약 ─────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"[완료] CSV → JSON 변환")
    print(f"  유효 학생 수       : {len(student_list)}명")
    print(f"  유효하지 않은 주소 : {len(invalid_list)}건")
    print(f"  중복 주소          : {len(duplicates)}건")
    print(f"  저장 경로          : {json_path}")
    print(f"{'='*50}")
    print(f"\n다음 단계:")
    print(f"  uv run python week01/2_2_distribute.py --dry-run")
    print(f"  uv run python week01/2_2_distribute.py")


if __name__ == "__main__":
    convert_csv_to_json()
