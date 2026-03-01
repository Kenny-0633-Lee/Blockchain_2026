import json
import os
import sys
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────
#  W01_2_distribute.py
#  students.json 을 읽어 Sepolia ETH를 학생들에게 일괄 전송합니다.
#
#  사용법:
#    uv run python W01_2_distribute.py            # 실제 전송
#    uv run python W01_2_distribute.py --dry-run  # 전송 없이 확인만
#
#  전제 조건:
#    - W01_1_convert.py 실행 완료 (00_Admin_Only/students.json 존재)
#    - 프로젝트 루트의 .env 파일에 INFURA_URL, PRIVATE_KEY 설정
#
#  재실행 안전성:
#    status="success" 인 학생은 자동으로 skip합니다.
#    중단 후 재실행해도 중복 전송되지 않습니다.
# ──────────────────────────────────────────────────────────

# .env 파일 로드 (스크립트 위치 기준 상위 폴더)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def distribute_eth(dry_run: bool = False):
    """
    students.json 을 읽어 Sepolia ETH를 일괄 전송합니다.

    Args:
        dry_run: True이면 실제 전송 없이 대상 목록과 예상 비용만 출력합니다.
    """
    base_path = Path(__file__).parent.parent / "00_Admin_Only"
    data_path = base_path / "students.json"

    # -- 환경변수 확인 --
    infura_url  = os.getenv("INFURA_URL")
    private_key = os.getenv("PRIVATE_KEY")

    print("--- [Debug Info] ---")
    if not infura_url:
        print("[Error] INFURA_URL을 읽지 못했습니다. .env 파일 위치나 오타를 확인하세요.")
        return
    print(f"Loaded INFURA_URL : {infura_url[:40]}...")   # 보안상 앞부분만 출력
    if not private_key:
        print("[Error] PRIVATE_KEY를 읽지 못했습니다.")
        return
    if dry_run:
        print("[Mode] DRY-RUN -- 실제 전송 없음")
    print("--------------------\n")

    # -- 네트워크 연결 --
    w3 = Web3(Web3.HTTPProvider(infura_url))
    try:
        if not w3.is_connected():
            print("[Error] Infura 연결 실패.")
            print("  원인 1: 인터넷 연결 상태 또는 학교 방화벽")
            print("  원인 2: INFURA_URL 오타 또는 API 키 미활성화")
            return
    except Exception as e:
        print(f"[Critical Error] 연결 중 예외 발생: {e}")
        return

    # -- 교수 계정 설정 --
    try:
        admin_account = w3.eth.account.from_key(private_key)
        admin_address = admin_account.address
    except Exception as e:
        print(f"[Error] 개인키 오류: {e}")
        return

    # -- 데이터 로드 --
    if not data_path.exists():
        print(f"[Error] {data_path} 없음.")
        print("  W01_1_convert.py를 먼저 실행하세요.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        students = json.load(f)

    pending      = [s for s in students if s.get("status") != "success"]
    already_done = len(students) - len(pending)

    # -- 잔액 및 예상 비용 계산 --
    balance_wei    = w3.eth.get_balance(admin_address)
    balance_eth    = float(w3.from_wei(balance_wei, 'ether'))
    gas_price_gwei = float(w3.from_wei(w3.eth.gas_price, 'gwei'))
    total_send     = sum(s['amount_eth'] for s in pending)
    est_gas_eth    = (21000 * gas_price_gwei * 1e-9 * 1.2) * len(pending)
    total_needed   = total_send + est_gas_eth

    print(f"[Info] 교수 계정  : {admin_address}")
    print(f"[Info] 현재 잔액  : {balance_eth:.4f} ETH")
    print(f"[Info] Gas Price  : {gas_price_gwei:.2f} gwei")
    print(f"[Info] 배포 대상  : {len(pending)}명  (이미 완료: {already_done}명 skip)")
    print(f"[Info] 전송 합계  : {total_send:.4f} ETH")
    print(f"[Info] 예상 가스비: {est_gas_eth:.6f} ETH")
    print(f"[Info] 총 필요량  : {total_needed:.4f} ETH")

    if balance_eth < total_needed:
        print(f"\n[Error] 잔액 부족!")
        print(f"  보유: {balance_eth:.4f} ETH  /  필요: {total_needed:.4f} ETH")
        print(f"  Sepolia Faucet -> https://sepoliafaucet.com")
        return

    # -- Dry-run 종료 --
    if dry_run:
        print("\n[DRY-RUN] 배포 예정 목록:")
        for i, s in enumerate(pending, 1):
            print(f"  {i:3}. {s['name']} ({s.get('student_id','')}) -> {s['wallet']}")
        print("\n[DRY-RUN] 실제 전송 없이 종료합니다.")
        return

    # -- 실제 배포 --
    print(f"\n[Info] 배포 시작...\n")
    nonce         = w3.eth.get_transaction_count(admin_address)
    success_count = 0

    for student in students:
        if student.get("status") == "success":
            print(f"[Skip] {student['name']} -- 이미 완료")
            continue

        amount_wei = w3.to_wei(student['amount_eth'], 'ether')
        print(f"[Pending] {student['name']} ({student['wallet'][:14]}...) -> {student['amount_eth']} ETH 전송 중...")

        try:
            tx = {
                'nonce':    nonce,
                'to':       student['wallet'],
                'value':    amount_wei,
                'gas':      21000,
                'gasPrice': int(w3.eth.gas_price * 1.2),  # 빠른 처리를 위해 가스비 20% 가산
                'chainId':  11155111                       # Sepolia Chain ID
            }
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            student["status"]  = "success"
            student["tx_hash"] = w3.to_hex(tx_hash)
            print(f" -> [Success] TX: {student['tx_hash']}")
            print(f"    https://sepolia.etherscan.io/tx/{student['tx_hash']}")

            nonce += 1
            success_count += 1

        except Exception as e:
            print(f" -> [Failed] {student['name']} 오류: {e}")

        # 전송 직후 즉시 JSON 저장 -- 중단 시에도 완료 학생 기록 보존
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(students, f, indent=4, ensure_ascii=False)

    print(f"\n[Done] 총 {success_count}명 배포 완료.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    distribute_eth(dry_run=dry)
