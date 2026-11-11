"""
07_ai_opml_verification/opml_demo.py  (특강 2026-11-25)
=======================================================
AI 추론을 체인에서 어떻게 검증하나? — 전부 다시 계산하지 않고 '이분 탐색'과 '불시 검사'로

Part A. opML 방식(낙관적 검증 + 분쟁 시 이분 탐색)
  - 오프체인 VM 이 1,024 단계를 실행하고 단계별 상태 해시를 남긴다.
  - 제출자가 중간(637단계)부터 값을 속였다. 도전자가 이분 탐색으로 '처음 어긋난 한 단계'를 찾는다.
  - 체인(스마트 컨트랙트)은 그 한 단계만 직접 실행해 판정한다.
Part B. 확률적 표본 검사(Proof of Sampling 아이디어, 단순화)
  - 속이면 이득 G, 걸리면 벌금 S. 검사 확률 p 가 G/(G+S) 보다 크면 속이는 게 손해.

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통, 저장소 루트에서)
  uv run python special_topic_2026/07_ai_opml_verification/opml_demo.py

※ 개념 시뮬레이션입니다. 실제 opML 은 MIPS VM 의 상태 Merkle root 로 이분 탐색하고, PoSP 는 스테이크·평판·중재 구조가 더 있습니다.
"""
import hashlib
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N = 1024


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def step(state: str, t: int) -> str:
    """VM 한 단계 (결정적 전이). 실제로는 행렬곱 등 연산 한 스텝에 해당"""
    return h(f"{state}|{t}|op{t % 7}".encode())


def run(init: str, cheat_from=None):
    """상태열 s[0..N]. cheat_from 단계부터는 틀린 전이를 하고 그 값에서 계속 진행"""
    s = [init]
    for t in range(N):
        nxt = step(s[-1], t)
        if cheat_from is not None and t == cheat_from:
            nxt = h(b"forged" + nxt.encode())
        s.append(nxt)
    return s


def part_a():
    print("=" * 66)
    print("Part A. opML: 1,024 단계 추론, 637단계에서 조작 -> 이분 탐색으로 적발")
    print("=" * 66)
    honest = run("input:cat.png")
    liar = run("input:cat.png", cheat_from=637)
    print(f"  제출자가 체인에 올린 결과 해시 : {liar[-1][:16]}…")
    print(f"  도전자가 직접 계산한 결과 해시 : {honest[-1][:16]}…   -> 불일치, 분쟁 개시")
    print(f"  체인이 전부 다시 계산하면 {N} 단계 (가스 폭발). 대신 이분 탐색:\n")

    lo, hi, rounds = 0, N, 0
    assert honest[lo] == liar[lo] and honest[hi] != liar[hi]
    while hi - lo > 1:
        mid = (lo + hi) // 2
        rounds += 1
        same = honest[mid] == liar[mid]
        print(f"  라운드 {rounds:>2}: 구간 [{lo:>4},{hi:>4}]  중간 {mid:>4}단계 상태 해시 "
              f"{'일치 -> 오른쪽' if same else '불일치 -> 왼쪽'}")
        lo, hi = (mid, hi) if same else (lo, mid)
    print(f"\n  {rounds}번 비교로 처음 어긋난 단계 = {lo} -> {hi}")
    ok = step(honest[lo], lo) == honest[hi]
    bad = step(liar[lo], lo) == liar[hi]
    print(f"  [체인의 1단계 재실행] 합의된 상태 s[{lo}] 에서 한 단계만 실행:")
    print(f"    도전자의 s[{hi}] 와 일치: {ok}    제출자의 s[{hi}] 와 일치: {bad}")
    print(f"  => 제출자 패배, 스테이크 몰수. 체인 비용: 해시 비교 {rounds}번 + 1단계 실행 (log2 {N} = {rounds}).")


def part_b():
    print("\n" + "=" * 66)
    print("Part B. 불시 검사: 속이는 게 이득이 되는 검사 확률은?")
    print("=" * 66)
    G, S = 1.0, 20.0  # 속여서 아끼는 계산비용 G, 적발 시 벌금 S (상대 단위)
    pstar = G / (G + S)
    print(f"  모델: 속이면 작업당 +{G} 이득, 걸리면 -{S} 벌금. 손익분기 검사 확률 p* = G/(G+S) = {pstar:.3f}")
    print(f"  {'p':>6} {'속임 기대이익':>12}  막대(+이익 / -손해)")
    for p in [0.00, 0.02, 0.04, 0.0476, 0.06, 0.10, 0.20]:
        ev = (1 - p) * G - p * S
        bar = ("#" * int(abs(ev) * 20)) if ev >= 0 else ("-" * int(abs(ev) * 20))
        print(f"  {p:>6.3f} {ev:>12.3f}  {'+' if ev >= 0 else '-'}{bar}")
    print("  -> p 가 p* 를 넘으면 정직하게 계산하는 편이 이득. 모든 작업을 재검사할 필요가 없다.")

    print("\n  시뮬레이션 (작업 10,000건, 검사확률 p):")
    random.seed(2026)
    for p in (0.02, 0.10):
        cheater = honest = 0.0
        first = None
        for t in range(10000):
            if random.random() < p:           # 이 작업이 감사됨
                if first is None:
                    first = t + 1
                cheater -= S                   # 속인 노드는 벌금
            else:
                cheater += G                   # 안 걸리면 아낀 비용만큼 이득
            honest += 0.0                      # 정직 노드는 기준(0)
        print(f"    p={p:.2f}: 속이는 노드 누적 {cheater:>9.1f}  vs 정직 노드 {honest:.1f}   "
              f"(첫 적발 {first}번째 작업)")
    print("  -> p=0.02(< p*)에서는 속이는 쪽이 이득, p=0.10(> p*)에서는 손해. 임계값 p* 가 설계의 핵심.")
    print("  ※ 적발 뒤에도 계속 속인다고 가정한 단순 모델. 실제는 적발 즉시 스테이크 몰수·퇴출,")
    print("     노드 평판·스테이크 비례 검사 확률, 분쟁 시 중재 라운드가 더 있다.")


if __name__ == "__main__":
    part_a()
    part_b()
