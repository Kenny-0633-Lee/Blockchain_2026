"""
week01/distribute_eth.py   [단일 파일 Set — All-in-One]
=======================================================
CSV 변환 + ETH 배포 통합 스크립트 (교수용)

[기존 2-file Set 과의 차이]
  기존 Set (2_1 + 2_2):
    - CSV 변환과 배포가 명확히 분리 → 단계별 검토 가능
    - 00_Admin_Only/ 폴더에 민감 데이터 격리
    - 실무적으로 권장하는 구조

  이 파일 (단일 파일):
    - CSV → 변환 → 배포를 한 명령으로 처리 → 빠른 실행
    - 설치/설정 파일이 적어 처음 사용에 편리
    - --dry-run / --from-csv / --json 옵션으로 유연하게 제어

실행 방법:
  # 1) CSV → 변환 → dry-run (계획 확인)
  uv run python week01/distribute_eth.py --from-csv students_raw.csv --dry-run

  # 2) CSV → 변환 → 실제 배포 (전체 파이프라인)
  uv run python week01/distribute_eth.py --from-csv students_raw.csv

  # 3) 기존 students.json 그대로 dry-run
  uv run python week01/distribute_eth.py --dry-run

  # 4) 기존 students.json 그대로 배포 (중단 후 재실행 안전)
  uv run python week01/distribute_eth.py

사전 준비:
  프로젝트 루트 .env:
    INFURA_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
    PRIVATE_KEY=0xYOUR_PRIVATE_KEY
  uv add web3 python-dotenv

⚠️  이 스크립트는 교수님만 실행합니다.
"""

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

try:
    from web3 import Web3
    from dotenv import load_dotenv
except ImportError:
    print("[Error] 필요 패키지 없음: uv add web3 python-dotenv")
    sys.exit(1)

# ── 설정 ─────────────────────────────────────────────────────
AMOUNT_ETH     = 0.1
GAS_LIMIT      = 21_000
GAS_MULTIPLIER = 1.2     # 가스비 20% 가산
TX_DELAY_SEC   = 2       # 트랜잭션 간 딜레이 (초)
SEPOLIA_CHAIN  = 11_155_111
CSV_ENCODING   = "utf-8-sig"

# Tally CSV 헤더 (폼 설정에 맞게 수정)
HEADER_NAME   = "이름"
HEADER_WALLET = "지갑주소(메타마스크)"

# 기본 경로
_ROOT          = Path(__file__).parent.parent
DEFAULT_ADMIN  = _ROOT / "00_Admin_Only"
DEFAULT_JSON   = _ROOT / "week01" / "students.json"


# ──────────────────────────────────────────────────────────────
# 1. 유틸리티
# ──────────────────────────────────────────────────────────────

def _is_valid_address(address: str) -> bool:
    if not (address.startswith("0x") and len(address) == 42):
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def _save_json(data: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────
# 2. CSV → student dict 변환
# ──────────────────────────────────────────────────────────────

def csv_to_students(csv_path: Path) -> list[dict]:
    """
    Tally CSV → student dict 리스트
    - 주소 유효성 검사 + 중복 주소 감지 포함
    """
    if not csv_path.exists():
        print(f"[Error] CSV 파일 없음: {csv_path}")
        sys.exit(1)

    student_list  = []
    invalid_list  = []
    address_count = Counter()

    with open(csv_path, encoding=CSV_ENCODING) as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            print(f"[Info] CSV 헤더: {list(reader.fieldnames)}")

        for row_num, row in enumerate(reader, start=2):
            name    = row.get(HEADER_NAME,   "").strip()
            address = row.get(HEADER_WALLET, "").strip()

            if not name and not address:
                continue

            address_count[address] += 1

            if _is_valid_address(address):
                student_list.append({
                    "name":       name,
                    "wallet":     address,
                    "status":     "pending",
                    "amount_eth": AMOUNT_ETH,
                    "tx_hash":    None,
                })
            else:
                invalid_list.append((row_num, name, address))
                print(f"[Warning] 유효하지 않은 주소 | 행 {row_num} | {name} | '{address}'")

    # 중복 감지
    duplicates = {a: c for a, c in address_count.items() if c > 1 and a}
    if duplicates:
        print(f"\n[Warning] 중복 지갑 주소 ({len(duplicates)}건):")
        for addr, cnt in duplicates.items():
            names = [s["name"] for s in student_list if s["wallet"] == addr]
            print(f"  {addr[:20]}...  ({cnt}회)  → {names}")

    print(f"[Info] CSV 변환 완료 — 유효: {len(student_list)}명 / 무효: {len(invalid_list)}건")
    return student_list


# ──────────────────────────────────────────────────────────────
# 3. 환경 변수 & Web3 초기화
# ──────────────────────────────────────────────────────────────

def setup_web3() -> tuple[Web3, str, str]:
    """환경 변수 로드 → Sepolia 연결 → (w3, sender, private_key)"""
    env_path = _ROOT / ".env"
    load_dotenv(dotenv_path=env_path)

    infura_url  = os.getenv("INFURA_URL",  "")
    private_key = os.getenv("PRIVATE_KEY", "")

    print("--- [환경 변수 확인] ---")
    if not infura_url:
        print("[Error] INFURA_URL 없음 — .env 확인")
        sys.exit(1)
    if not private_key:
        print("[Error] PRIVATE_KEY 없음 — .env 확인")
        sys.exit(1)
    print(f"  INFURA_URL  : {infura_url[:35]}...")
    print("  PRIVATE_KEY : [로드됨 — 보안상 미출력]")
    print("-" * 24)

    w3 = Web3(Web3.HTTPProvider(infura_url))
    if not w3.is_connected():
        print("[Error] Sepolia 연결 실패 — INFURA_URL 또는 네트워크 확인")
        sys.exit(1)
    print(f"[Info] Sepolia 연결 성공 | 최신 블록: {w3.eth.block_number:,}")

    try:
        account = w3.eth.account.from_key(private_key)
    except Exception as e:
        print(f"[Error] 개인키 오류: {e}")
        sys.exit(1)

    return w3, account.address, private_key


# ──────────────────────────────────────────────────────────────
# 4. Dry-run 보고서
# ──────────────────────────────────────────────────────────────

def dry_run_report(students: list[dict], w3: Web3, sender: str) -> None:
    """실제 트랜잭션 없이 배포 계획 전체 출력"""
    pending   = [s for s in students if s.get("status") != "success"]
    done      = [s for s in students if s.get("status") == "success"]
    total_eth = sum(s["amount_eth"] for s in pending)
    balance   = float(w3.from_wei(w3.eth.get_balance(sender), "ether"))
    gas_gwei  = float(w3.from_wei(w3.eth.gas_price, "gwei"))

    print(f"\n{'='*58}")
    print("  🔎  DRY-RUN — 실제 트랜잭션은 전송되지 않습니다")
    print(f"{'='*58}")
    print(f"  발신 지갑  : {sender}")
    print(f"  현재 잔액  : {balance:.4f} ETH")
    print(f"  현재 가스  : {gas_gwei:.2f} Gwei  (× {GAS_MULTIPLIER} 가산)")
    print(f"\n  이미 완료  : {len(done)}명  (skip 예정)")
    _per = pending[0]["amount_eth"] if pending else AMOUNT_ETH
    print(f"  전송 예정  : {len(pending)}명  × {_per} ETH  = {total_eth:.3f} ETH 필요")

    if balance < total_eth:
        print(f"\n  ⚠️  잔액 부족!  {total_eth - balance:.4f} ETH 추가 필요")
    else:
        print(f"\n  ✅  잔액 충분  (여유: {balance - total_eth:.4f} ETH)")

    print(f"\n  {'No':>3}  {'이름':12}  {'지갑 주소(앞 20자)':22}  {'금액':>8}  상태")
    print("  " + "-" * 62)
    for i, s in enumerate(students, 1):
        tag    = "✓ skip" if s.get("status") == "success" else "→ 전송"
        amount = f"{s['amount_eth']} ETH"
        print(f"  {i:3d}  {s['name']:12}  {s['wallet'][:20]}...  {amount:>8}  {tag}")

    print(f"{'='*58}")
    print("  실제 실행: uv run python week01/distribute_eth.py")
    print(f"{'='*58}\n")


# ──────────────────────────────────────────────────────────────
# 5. 실제 배포
# ──────────────────────────────────────────────────────────────

def distribute(
    students:    list[dict],
    w3:          Web3,
    sender:      str,
    private_key: str,
    save_path:   Path,
) -> None:
    """
    ETH 일괄 전송
    - status="success" 는 자동 skip (재실행 안전)
    - 트랜잭션마다 즉시 JSON 저장 (중단 시 소실 방지)
    - 가스비 × GAS_MULTIPLIER 가산
    """
    pending = [s for s in students if s.get("status") != "success"]
    if not pending:
        print("[Info] 전송 대상 없음 (모두 완료 상태)")
        return

    balance   = float(w3.from_wei(w3.eth.get_balance(sender), "ether"))
    total_eth = sum(s["amount_eth"] for s in pending) * 1.05
    if balance < total_eth:
        print(f"[Error] 잔액 부족 ({balance:.4f} ETH < 필요 {total_eth:.4f} ETH)")
        sys.exit(1)

    print(f"\n[Info] 발신 지갑  : {sender}")
    print(f"[Info] 현재 잔액  : {balance:.4f} ETH")
    print(f"[Info] 가스비     : {w3.from_wei(w3.eth.gas_price, 'gwei'):.2f} Gwei × {GAS_MULTIPLIER}")
    print(f"[Info] 전송 대상  : {len(pending)}명\n")

    gas_price     = int(w3.eth.gas_price * GAS_MULTIPLIER)
    nonce         = w3.eth.get_transaction_count(sender)
    success_count = 0

    for student in students:
        if student.get("status") == "success":
            print(f"[Skip] {student['name']} — 이미 완료 ({(student.get('tx_hash') or '')[:16]}...)")
            continue

        name    = student["name"]
        to_addr = student["wallet"]
        amount  = student["amount_eth"]

        print(f"[Pending] {name:10}  ({to_addr[:14]}...)  → {amount} ETH ...", end="", flush=True)

        try:
            tx = {
                "nonce":    nonce,
                "to":       to_addr,
                "value":    w3.to_wei(amount, "ether"),
                "gas":      GAS_LIMIT,
                "gasPrice": gas_price,
                "chainId":  SEPOLIA_CHAIN,
            }
            signed   = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash  = w3.eth.send_raw_transaction(signed.raw_transaction)

            student["status"]  = "success"
            student["tx_hash"] = w3.to_hex(tx_hash)
            print(f" ✓  TX: {student['tx_hash'][:22]}...")
            nonce         += 1
            success_count += 1

        except Exception as e:
            student["status"] = "failed"
            print(f" ✗  오류: {e}")

        # ▶ 트랜잭션마다 즉시 저장 (중단 시 성공 기록 보존)
        _save_json(students, save_path)
        time.sleep(TX_DELAY_SEC)

    print(f"\n{'='*55}")
    print(f"[Done] {success_count}/{len(pending)}명 전송 완료")
    print(f"  결과 파일 : {save_path}")
    print(f"  Etherscan : https://sepolia.etherscan.io/address/{sender}")
    print(f"{'='*55}")


# ──────────────────────────────────────────────────────────────
# 6. CLI 진입점
# ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Week01 ETH 배포 스크립트 (교수용) — 단일 파일 버전",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
실행 예시:
  # CSV 읽어 dry-run (계획 확인)
  uv run python week01/distribute_eth.py --from-csv students_raw.csv --dry-run

  # CSV 읽어 실제 배포
  uv run python week01/distribute_eth.py --from-csv students_raw.csv

  # 기존 JSON 으로 dry-run
  uv run python week01/distribute_eth.py --dry-run

  # 기존 JSON 으로 배포 (중단 후 재실행 안전)
  uv run python week01/distribute_eth.py
        """,
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="실제 전송 없이 배포 계획만 출력",
    )
    p.add_argument(
        "--from-csv", metavar="FILE",
        help="00_Admin_Only/<FILE> CSV 에서 변환 후 실행  (예: students_raw.csv)",
    )
    p.add_argument(
        "--json", metavar="FILE", default=str(DEFAULT_JSON),
        help=f"students.json 경로 (기본: {DEFAULT_JSON})",
    )
    return p


def main() -> None:
    args      = build_parser().parse_args()
    dry       = args.dry_run
    json_path = Path(args.json)

    # ── 학생 데이터 로드 ──────────────────────────────────────
    if args.from_csv:
        csv_path  = DEFAULT_ADMIN / args.from_csv
        students  = csv_to_students(csv_path)
        # CSV 에서 변환 시 저장 위치를 00_Admin_Only/ 로 고정
        json_path = DEFAULT_ADMIN / "students.json"
        _save_json(students, json_path)
        print(f"[Info] JSON 저장: {json_path}\n")
    else:
        if not json_path.exists():
            print(f"[Error] students.json 없음: {json_path}")
            print("  → --from-csv 로 CSV 에서 생성하거나 수동으로 JSON 작성")
            sys.exit(1)
        with open(json_path, encoding="utf-8") as f:
            students = json.load(f)

    print(f"[Info] 로드된 학생 수: {len(students)}명\n")

    # ── Web3 초기화 ───────────────────────────────────────────
    w3, sender, private_key = setup_web3()

    # ── 실행 분기 ─────────────────────────────────────────────
    if dry:
        dry_run_report(students, w3, sender)
    else:
        distribute(students, w3, sender, private_key, json_path)


if __name__ == "__main__":
    main()
