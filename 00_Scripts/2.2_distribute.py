import json
import os
import sys
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일이 프로젝트 루트에 있어야 함)
# 스크립트 위치 기준으로 상위 폴더의 .env를 명시적으로 찾습니다.
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def distribute_eth():
    """
    students.json 리스트를 읽어 Sepolia ETH를 일괄 전송합니다.
    연결 오류를 진단하기 위한 디버깅 코드가 포함되어 있습니다.
    """
    
    # 경로 설정 (00_Admin_Only 폴더 내의 students.json)
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    data_path = base_path / "students.json"
    
    # --- 디버깅 섹션: 설정값 확인 ---
    infura_url = os.getenv("INFURA_URL")
    private_key = os.getenv("PRIVATE_KEY")

    print("--- [Debug Info] ---")
    if not infura_url:
        print("[Error] .env 파일에서 INFURA_URL을 읽어오지 못했습니다. 파일 위치나 오타를 확인해 주세요.")
        return
    else:
        print(f"Loaded INFURA_URL: {infura_url[:30]}...") # 보안을 위해 앞부분만 출력
    
    if not private_key:
        print("[Error] .env 파일에서 PRIVATE_KEY를 읽어오지 못했습니다.")
        return
    print("--------------------")
    # ----------------------------

    # 이더리움 노드 연결 시도
    w3 = Web3(Web3.HTTPProvider(infura_url))
    
    try:
        if not w3.is_connected():
            print("[Error] 이더리움 네트워크(Infura) 연결에 실패했습니다.")
            print("원인 후보 1: 인터넷 연결 상태나 학교 방화벽 문제")
            print("원인 후보 2: Infura API 키가 활성화되지 않았거나 URL 오타")
            return
    except Exception as e:
        print(f"[Critical Error] 연결 중 예외 발생: {e}")
        return

    # 교수님 계정 설정
    try:
        admin_account = w3.eth.account.from_key(private_key)
        admin_address = admin_account.address
    except Exception as e:
        print(f"[Error] 개인키가 올바르지 않습니다: {e}")
        return

    # 배포 대상 데이터 로드
    if not data_path.exists():
        print(f"[Error] {data_path} 파일이 없습니다. 2.1_convert.py를 먼저 실행해 주세요.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        students = json.load(f)

    print(f"\n[Info] 배포 시작 계정: {admin_address}")
    print(f"[Info] 현재 가스비(Gas Price): {w3.from_wei(w3.eth.gas_price, 'gwei')} gwei")
    
    # 현재 논스(Nonce) 값 가져오기
    nonce = w3.eth.get_transaction_count(admin_address)

    success_count = 0
    for student in students:
        if student.get("status") == "success":
            print(f"[Skip] {student['name']} 학생은 이미 전송 완료되었습니다.")
            continue

        target_address = student["wallet"]
        amount_eth = student["amount_eth"]
        amount_wei = w3.to_wei(amount_eth, 'ether')

        print(f"[Pending] {student['name']} ({target_address})에게 {amount_eth} ETH 전송 중...")

        try:
            # 트랜잭션 구성
            tx = {
                'nonce': nonce,
                'to': target_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': int(w3.eth.gas_price * 1.2), # 빠른 처리를 위해 가스비 20% 가산
                'chainId': 11155111  # Sepolia Chain ID
            }

            # 트랜잭션 서명 및 전송
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # 상태 업데이트
            student["status"] = "success"
            student["tx_hash"] = w3.to_hex(tx_hash)
            print(f" -> [Success] TX Hash: {student['tx_hash']}")
            
            nonce += 1 # 다음 전송을 위해 논스 증가
            success_count += 1

        except Exception as e:
            print(f" -> [Failed] {student['name']} 전송 오류: {e}")

    # 결과 반영하여 students.json 업데이트
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4, ensure_ascii=False)
    
    print(f"\n[Done] 총 {success_count}명의 학생에게 배포를 완료했습니다.")

if __name__ == "__main__":
    distribute_eth()