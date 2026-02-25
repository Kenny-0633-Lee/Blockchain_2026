import csv
import json
from pathlib import Path

def convert_csv_to_json(input_file: str, output_file: str):
    """
    Tally에서 수집된 한글 헤더 CSV를 관리용 JSON으로 변환합니다.
    """
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    csv_path = base_path / input_file
    json_path = base_path / output_file

    if not csv_path.exists():
        print(f"[Error] Source file not found: {csv_path}")
        return

    student_list = []

    try:
        # Tally CSV는 보통 utf-8-sig 또는 utf-8을 사용합니다.
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Tally 실제 헤더 이름으로 수정
                name = row.get('이름', '').strip()
                address = row.get('지갑주소(메타마스크)', '').strip()

                # 주소 유효성 검사 (0x로 시작하고 42자리인지 확인)
                if address.startswith('0x') and len(address) == 42:
                    student_list.append({
                        "name": name,
                        "wallet": address,
                        "status": "pending",
                        "amount_eth": 0.1
                    })
                else:
                    # 유효하지 않은 경우 경고 메시지 출력
                    print(f"[Warning] Invalid wallet address for: {name} ({address})")

        # 정제된 데이터를 JSON 파일로 저장
        with open(json_path, mode='w', encoding='utf-8') as f:
            json.dump(student_list, f, indent=4, ensure_ascii=False)
        
        print(f"[Success] Processed {len(student_list)} students.")
        print(f"[Info] JSON saved to: {json_path}")

    except Exception as e:
        print(f"[Critical Error] {e}")

if __name__ == "__main__":
    convert_csv_to_json('students_raw.csv', 'students.json')