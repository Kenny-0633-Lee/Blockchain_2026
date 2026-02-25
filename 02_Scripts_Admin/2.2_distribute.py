import json
import os
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# .env 파일로부터 환경 변수 로드
load_dotenv()

def distribute_eth():
    """
    students.json 리스트를 읽어 Sepolia ETH를 일괄 전송합니다.
    관리자용 도구이므로 한글 주석을 유지합니다.
    """
    # 경로 설정
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    data_path = base_path / "students.json"
    
    # 이더리움 노드 연결 확인 (Infura)
    w3 = Web3(Web3.HTTPProvider(os.getenv("INFURA_URL")))
    if not w3.is_connected():
        print("[Error] Failed to connect to Ethereum network.")
        return

    # 교수님 계정 설정
    private_key = os.getenv("PRIVATE_KEY")
    admin_account = w3.eth.account.from_key(private_key)
    admin_address = admin_account.address

    # 배포 대상 데이터 로드
    with open(data_path, 'r', encoding='utf-8') as f:
        students = json.load(f)

    print(f"[Info] Starting distribution from: {admin_address}")
    
    for student in students:
        if student["status"] == "success":
            continue  # 이미 전송 성공한 경우 건너뜀

        target_address = student["wallet"]
        amount_wei = w3.to_wei(student["amount_eth"], 'ether')

        # 트랜잭션 구성
        tx = {
            'nonce': w3.eth.get_transaction_count(admin_address),
            'to': target_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 11155111  # Sepolia Chain ID
        }

        # 트랜잭션 서명 및 전송
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # 상태 업데이트
        student["status"] = "success"
        student["tx_hash"] = w3.to_hex(tx_hash)
        print(f"[Success] Sent to {student['name']}: {w3.to_hex(tx_hash)}")

    # 결과 반영하여 students.json 업데이트
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    distribute_eth()