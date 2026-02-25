import csv
import json
from pathlib import Path

def convert_csv_to_json(input_file: str, output_file: str):
    """
    수강생 지갑 주소 데이터를 자동 배포용 JSON 형식으로 변환합니다.
    관리자용 스크립트이므로 한글 주석을 사용합니다.
    """
    # 경로 설정: 스크립트는 02_Scripts_Admin에 있고, 데이터는 00_Admin_Only에 있음
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    csv_path = base_path / input_file
    json_path = base_path / output_file

    if not csv_path.exists():
        print(f"[오류] 원본 파일을 찾을 수 없습니다: {csv_path}")
        return

    student_list = []

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            # CSV 헤더는 name, wallet으로 가정함
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name', '').strip()
                address = row.get('wallet', '').strip()

                # 이더리움 주소 유효성 검사 (0x로 시작하고 42자리인지 확인)
                if address.startswith('0x') and len(address) == 42:
                    student_list.append({
                        "name": name,
                        "wallet": address,
                        "status": "pending",
                        "amount_eth": 0.1  # 기본 배포 수량
                    })
                else:
                    print(f"[경고] {name} 학생의 지갑 주소가 유효하지 않습니다: {address}")

        # 정제된 데이터를 JSON 파일로 저장
        with open(json_path, mode='w', encoding='utf-8') as f:
            json.dump(student_list, f, indent=4, ensure_ascii=False)
        
        print(f"[성공] 총 {len(student_list)}명의 수강생 데이터를 처리했습니다.")
        print(f"[안내] 결과 저장 경로: {json_path}")

    except Exception as e:
        print(f"[치명적 오류] 데이터 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    # 파일 변환 실행
    convert_csv_to_json('students_raw.csv', 'students.json')