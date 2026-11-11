"""
02_pow_mining/pow_demo.py  (특강 2026-11-25)
============================================
Proof of Work: '해시가 0 으로 시작하는 nonce 찾기' 와 '과거 블록을 고치려면 다시 캐야 한다'

보여줄 것
  1) 난이도(앞자리 0 개수)별 채굴 시도 횟수/시간: 한 자리 올릴 때마다 약 16배
  2) 블록 3개를 캔 뒤, 첫 블록을 변조하면 뒤 블록이 모두 무효 -> 다시 캐는 비용
  3) 정직한 체인이 계속 자라는 동안 공격자는 따라잡기 어렵다는 감각

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통, 저장소 루트에서)
  uv run python special_topic_2026/02_pow_mining/pow_demo.py
  uv run python special_topic_2026/02_pow_mining/pow_demo.py --max-diff 6   # 시간이 남을 때 (6자리는 수십 초)
"""
import hashlib
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MAX_DIFF = 5
if "--max-diff" in sys.argv:
    MAX_DIFF = int(sys.argv[sys.argv.index("--max-diff") + 1])


def block_hash(prev: str, data: str, nonce: int) -> str:
    return hashlib.sha256(f"{prev}|{data}|{nonce}".encode()).hexdigest()


def mine(prev: str, data: str, diff: int):
    target = "0" * diff
    nonce, t0 = 0, time.perf_counter()
    while True:
        hx = block_hash(prev, data, nonce)
        if hx.startswith(target):
            return nonce, hx, time.perf_counter() - t0
        nonce += 1


def main():
    print("[1] 난이도별 채굴 (난이도마다 새 블록 5회 평균 / 5자리는 3회)")
    print(f"  {'난이도':>4} {'평균 시도':>12} {'기대값 16^d':>12} {'평균 시간(s)':>12}")
    rate_n, rate_t = 0, 0.0
    for d in range(1, MAX_DIFF + 1):
        trials = 5 if d <= 4 else 3
        tries, secs = [], []
        for k in range(trials):
            nonce, hx, sec = mine("genesis", f"Alice->Bob 1BTC #{d}-{k}", d)
            tries.append(nonce + 1)
            secs.append(sec)
        rate_n += sum(tries)
        rate_t += sum(secs)
        print(f"  {d:>4} {sum(tries) / trials:>12,.0f} {16 ** d:>12,} {sum(secs) / trials:>12.3f}")
    if rate_t > 0.05:
        rate = rate_n / rate_t
        print(f"  이 컴퓨터(파이썬)의 해시 속도 약 {rate / 1e6:.2f} MH/s")
        print(f"  같은 컴퓨터로 난이도 8 은 평균 약 {16 ** 8 / rate / 60:.0f} 분, 난이도 10 은 약 {16 ** 10 / rate / 3600:.0f} 시간.")
    print("  -> 한 자리마다 약 16배 (평균). 운이 좋으면 한 번에 맞을 수도 있어 5회 평균을 썼다.")

    print("\n[2] 블록 3개를 캔 뒤 첫 블록을 변조")
    diff = 4
    chain, prev = [], "0" * 64
    for i, data in enumerate(["B1: Alice->Bob 5", "B2: Bob->Carol 2", "B3: Carol->Dave 1"]):
        nonce, hx, sec = mine(prev, data, diff)
        chain.append({"data": data, "prev": prev, "nonce": nonce, "hash": hx, "sec": sec})
        print(f"  블록{i + 1} 채굴: 시도 {nonce + 1:>7,}회  hash={hx[:16]}…")
        prev = hx

    def valid(c):
        p = "0" * 64
        for b in c:
            if b["prev"] != p or block_hash(b["prev"], b["data"], b["nonce"]) != b["hash"] \
                    or not b["hash"].startswith("0" * diff):
                return False
            p = b["hash"]
        return True

    print(f"\n  변조 전 체인 유효: {valid(chain)}")
    chain[0]["data"] = "B1: Alice->Bob 500"  # 금액 변조
    print(f"  B1 금액 변조 후 유효: {valid(chain)}  (B1 해시가 달라져 PoW 조건·연결이 깨진다)")

    print("\n  공격자가 체인을 '다시 맞추려면' B1 부터 전부 재채굴해야 한다:")
    prev, redo, redo_tries = "0" * 64, [], 0
    for b in chain:
        nonce, hx, sec = mine(prev, b["data"], diff)
        redo.append({**b, "prev": prev, "nonce": nonce, "hash": hx})
        redo_tries += nonce + 1
        prev = hx
    orig_tries = sum(b["nonce"] + 1 for b in chain)
    print(f"  재채굴 시도 합계 {redo_tries:,}회 (블록 3개), 재구성 후 유효: {valid(redo)}")
    print(f"  (원래 정직한 채굴 {orig_tries:,}회 정도의 일을, 변조 시점 이후에 더 쌓인 블록 수만큼 추가로 해야 한다)")
    print("  -> 변조 비용 = (변조한 블록 이후의 블록 수) x 난이도. 확인 6블록 관례의 이유.")
    print("  ※ 한 대의 노트북 시연일 뿐. 실제 공격은 전체 네트워크 해시파워의 과반(51%)이 필요.")


if __name__ == "__main__":
    main()
