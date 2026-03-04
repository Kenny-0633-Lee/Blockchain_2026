"""
week01/2_2_distribute.py   [기존 Set — STEP 2/2]
================================================
students.json → Sepolia ETH 일괄 전송 (교수용)

역할:
  - 2_1_convert.py 가 생성한 students.json 을 읽어 ETH 일괄 전송
  - status="success" 학생은 자동 skip → 재실행 안전 (idempotent)
  - 전송 결과를 students.json 에 트랜잭션마다 즉시 기록   ← v0.2 수정
  - --dry-run 으로 실제 전송 없이 사전 검증 가능           ← v0.2 추가

실행:
  uv run python week01/2_2_distribute.py --dry-run  # 시뮬레이션
  uv run python week01/2_2_distribute.py            # 실제 전송

사전 준비:
  - 프로젝트 루트 .env:
      INFURA_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
      PRIVATE_KEY=0xYOUR_PRIVATE_KEY
  - uv add web3 python-dotenv

⚠️  이 스크립트는 교수님만 실행합니다.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    from web3 import Web3
    from dotenv import load_dotenv
except ImportError:
    print("[Error] 필요 패키지 없음: uv add web3 python-dotenv")
    sys.exit(1)

# ── 설정 ─────────────────────────────────────────────────────
GAS_LIMIT      = 21_000
GAS_MULTIPLIER = 1.2    # 가스비 20% 가산 → 빠른 처리
TX_DELAY_SEC   = 2      # 트랜잭션 간 딜레이 (초)
SEPOLIA_CHAIN  = 11_155_111

# 경로 설정
_BASE     = Path(__file__).parent.parent / "00_Admin_Only"
DATA_PATH = _BASE / "students.json"
ENV_PATH  = Path(__file__).parent.parent / ".env"


# ── 환경 변수 로드 ────────────────────────────────────────────

def _load_env() -> tuple[str, str]:
    load_dotenv(dotenv_path=ENV_PATH)
    infura_url  = os.getenv("INFURA_URL",  "")
    private_key = os.getenv("PRIVATE_KEY", "")

    print("--- [Debug Info] ---")
    if not infura_url:
        print("[Error] .env 에서 INFURA_URL 을 읽지 못했습니다.")
        sys.exit(1)
    print(f"Loaded INFURA_URL : {infura_url[:35]}...")   # 보안상 앞부분만

    if not private_key:
        print("[Error] .env 에서 PRIVATE_KEY 를 읽지 못했습니다.")
        sys.exit(1)
    print("PRIVATE_KEY       : [로드됨 — 보안상 미출력]")
    print("--------------------")
    return infura_url, private_key


# ── Web3 연결 ─────────────────────────────────────────────────

def _connect(infura_url: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(infura_url))
    try:
        if not w3.is_connected():
            raise ConnectionError
    except Exception:
        print("[Error] 이더리움 네트워크(Infura) 연결 실패.")
        print("  원인 후보 1: 인터넷 연결 상태나 학교 방화벽 문제")
        print("  원인 후보 2: Infura API 키가 활성화되지 않았거나 URL 오타")
        sys.exit(1)
    print(f"[Info] Sepolia 연결 성공 | 최신 블록: {w3.eth.block_number:,}")
    return w3


# ── JSON 저장 ─────────────────────────────────────────────────

def _save(students: list[dict]) -> None:
    """students.json 즉시 덮어쓰기 — 중단되어도 진행 상황 보존"""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4, ensure_ascii=False)


# ── Dry-run ───────────────────────────────────────────────────

def _dry_run(students: list[dict], w3: Web3, admin_address: str) -> None:
    """실제 트랜잭션 없이 배포 계획을 출력"""
    pending   = [s for s in students if s.get("status") != "success"]
    done      = [s for s in students if s.get("status") == "success"]
    total_eth = sum(s["amount_eth"] for s in pending)
    balance   = float(w3.from_wei(w3.eth.get_balance(admin_address), "ether"))
    gas_gwei  = float(w3.from_wei(w3.eth.gas_price, "gwei"))

    print(f"\n{'='*55}")
    print("  🔎  DRY-RUN 모드 — 실제 트랜잭션은 전송되지 않습니다")
    print(f"{'='*55}")
    print(f"  발신 지갑  : {admin_address}")
    print(f"  현재 잔액  : {balance:.4f} ETH")
    print(f"  현재 가스  : {gas_gwei:.2f} Gwei  (× {GAS_MULTIPLIER} 가산 적용)")
    print(f"\n  이미 완료  : {len(done)}명  (skip 예정)")
    print(f"  전송 예정  : {len(pending)}명  × {pending[0]['amount_eth'] if pending else 0} ETH"
          f"  = {total_eth:.3f} ETH 필요")

    if balance < total_eth:
        print(f"\n  ⚠️  잔액 부족!  {total_eth - balance:.4f} ETH 추가 필요")
    else:
        print(f"\n  ✅  잔액 충분  (여유: {balance - total_eth:.4f} ETH)")

    print(f"\n  {'No':>3}  {'이름':12}  {'지갑 주소(앞 20자)':22}  {'금액':>8}  상태")
    print("  " + "-" * 60)
    for i, s in enumerate(students, 1):
        tag    = "✓ skip" if s.get("status") == "success" else "→ 전송"
        amount = f"{s['amount_eth']} ETH"
        print(f"  {i:3d}  {s['name']:12}  {s['wallet'][:20]}...  {amount:>8}  {tag}")

    print(f"{'='*55}")
    print("  실제 실행: uv run python week01/2_2_distribute.py")
    print(f"{'='*55}\n")


# ── 실제 배포 ─────────────────────────────────────────────────

def distribute_eth(w3: Web3, admin_address: str, private_key: str) -> None:
    """
    students.json → ETH 일괄 전송

    v0.2 수정:
      - 트랜잭션마다 즉시 JSON 저장 (루프 끝 일괄저장 버그 수정)
        → 중간에 스크립트가 중단되어도 성공한 tx_hash 가 보존됨
    """
    if not DATA_PATH.exists():
        print(f"[Error] {DATA_PATH} 없음 — 2_1_convert.py 를 먼저 실행하세요.")
        sys.exit(1)

    with open(DATA_PATH, encoding="utf-8") as f:
        students = json.load(f)

    pending = [s for s in students if s.get("status") != "success"]
    if not pending:
        print("[Info] 전송 대상 없음 (모두 완료 상태)")
        return

    # 잔액 검사
    balance   = float(w3.from_wei(w3.eth.get_balance(admin_address), "ether"))
    total_eth = sum(s["amount_eth"] for s in pending) * 1.05   # 5% 가스 버퍼
    if balance < total_eth:
        print(f"[Error] 잔액 부족 ({balance:.4f} ETH < 필요 {total_eth:.4f} ETH)")
        sys.exit(1)

    print(f"\n[Info] 배포 시작 계정   : {admin_address}")
    print(f"[Info] 현재 잔액        : {balance:.4f} ETH")
    print(f"[Info] 가스비(Gas Price): {w3.from_wei(w3.eth.gas_price, 'gwei'):.2f} Gwei  × {GAS_MULTIPLIER}")
    print(f"[Info] 전송 대상        : {len(pending)}명\n")

    gas_price     = int(w3.eth.gas_price * GAS_MULTIPLIER)
    nonce         = w3.eth.get_transaction_count(admin_address)
    success_count = 0

    for student in students:
        if student.get("status") == "success":
            print(f"[Skip] {student['name']} — 이미 완료 ({(student.get('tx_hash') or '')[:16]}...)")
            continue

        name       = student["name"]
        to_address = student["wallet"]
        amount_eth = student["amount_eth"]
        amount_wei = w3.to_wei(amount_eth, "ether")

        print(f"[Pending] {name} ({to_address[:14]}...) → {amount_eth} ETH ...", end="", flush=True)

        try:
            tx = {
                "nonce":    nonce,
                "to":       to_address,
                "value":    amount_wei,
                "gas":      GAS_LIMIT,
                "gasPrice": gas_price,
                "chainId":  SEPOLIA_CHAIN,
            }
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            student["status"]  = "success"
            student["tx_hash"] = w3.to_hex(tx_hash)
            print(f" ✓  TX: {student['tx_hash'][:22]}...")
            nonce         += 1
            success_count += 1

        except Exception as e:
            student["status"] = "failed"
            print(f" ✗  오류: {e}")

        # ▶ 트랜잭션마다 즉시 저장 (v0.2 수정 — 중단 시 소실 방지)
        _save(students)
        time.sleep(TX_DELAY_SEC)

    # ── 최종 요약 ─────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"[Done] {success_count}/{len(pending)}명 전송 완료")
    print(f"  결과 파일 : {DATA_PATH}")
    print(f"  Etherscan : https://sepolia.etherscan.io/address/{admin_address}")
    print(f"{'='*55}")


# ── 진입점 ───────────────────────────────────────────────────

def main() -> None:
    dry_run = "--dry-run" in sys.argv

    infura_url, private_key = _load_env()
    w3                      = _connect(infura_url)

    try:
        admin_account = w3.eth.account.from_key(private_key)
        admin_address = admin_account.address
    except Exception as e:
        print(f"[Error] 개인키가 올바르지 않습니다: {e}")
        sys.exit(1)

    if dry_run:
        if not DATA_PATH.exists():
            print(f"[Error] {DATA_PATH} 없음 — 2_1_convert.py 를 먼저 실행하세요.")
            sys.exit(1)
        with open(DATA_PATH, encoding="utf-8") as f:
            students = json.load(f)
        _dry_run(students, w3, admin_address)
    else:
        distribute_eth(w3, admin_address, private_key)


if __name__ == "__main__":
    main()
