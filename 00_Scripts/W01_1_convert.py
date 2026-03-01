import csv
import json
from pathlib import Path

# ──────────────────────────────────────────────────────────
#  W01_1_convert.py
#  Tally Connect Wallet 방식으로 수집된 CSV를 관리용 JSON으로 변환합니다.
#
#  사용법:
#    uv run python W01_1_convert.py
#
#  전제 조건:
#    - 00_Admin_Only/students_raw.csv  (Tally Export CSV)
#  출력:
#    - 00_Admin_Only/students.json
#
#  ⚠️  주의: Tally Connect Wallet 컬럼명은 폼 설정에 따라 다를 수 있습니다.
#    첫 실행 시 출력되는 [CSV 컬럼 목록]을 확인하고,
#    필요하면 아래 address fallback 순서의 키를 실제 컬럼명으로 수정하세요.
# ──────────────────────────────────────────────────────────

def convert_csv_to_json(input_file: str, output_file: str):
    """
    Tally Connect Wallet CSV -> students.json 변환

    Tally Connect Wallet 사용 시 지갑 주소는 자동 수집됩니다.
    학생은 이름·학번만 직접 입력하고, 주소는 MetaMask 연결로 자동 전달됩니다.
    """
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    csv_path  = base_path / input_file
    json_path = base_path / output_file

    if not csv_path.exists():
        print(f"[Error] 원본 파일 없음: {csv_path}")
        print("  Tally 관리자 화면 -> Export -> CSV로 다운로드 후 위 경로에 저장하세요.")
        return

    student_list = []
    skipped      = []

    try:
        # Tally CSV는 보통 utf-8-sig (Windows BOM 포함) 또는 utf-8 인코딩
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # -- 첫 실행 시 실제 컬럼명 확인 --
            print(f"[Info] CSV 컬럼 목록: {reader.fieldnames}")
            print("       위 컬럼명이 아래 get() 키와 다르면 코드를 수정하세요.\n")

            for row in reader:
                name       = row.get('이름', '').strip()
                student_id = row.get('학번', '').strip()

                # Tally Connect Wallet: 폼 설정에 따라 컬럼명이 다를 수 있어
                # 아래 순서로 fallback 시도합니다.
                address = (
                    row.get('Wallet Address', '')        # Tally 영문 기본값
                    or row.get('wallet_address', '')     # 소문자 변형
                    or row.get('지갑주소', '')            # 한글 커스텀 레이블
                    or row.get('지갑주소(메타마스크)', '')  # 구버전 호환
                ).strip()

                # 주소 유효성 검사: 0x로 시작하고 42자리인지 확인
                if address.startswith('0x') and len(address) == 42:
                    student_list.append({
                        "name":       name,
                        "student_id": student_id,
                        "wallet":     address,
                        "status":     "pending",
                        "amount_eth": 0.1,
                        "tx_hash":    None
                    })
                else:
                    print(f"[Warning] 유효하지 않은 주소 -- {name} ({student_id}): '{address}'")
                    skipped.append(f"{name}({student_id})")

        # 정제된 데이터를 JSON으로 저장
        with open(json_path, mode='w', encoding='utf-8') as f:
            json.dump(student_list, f, indent=4, ensure_ascii=False)

        print(f"[Success] 처리 완료: {len(student_list)}명 -> {json_path}")
        if skipped:
            print(f"[Warning] 주소 오류로 제외된 학생 {len(skipped)}명: {', '.join(skipped)}")
            print("          해당 학생은 Tally 폼에서 Connect Wallet을 다시 하도록 안내하세요.")

    except Exception as e:
        print(f"[Critical Error] {e}")


if __name__ == "__main__":
    convert_csv_to_json('students_raw.csv', 'students.json')
