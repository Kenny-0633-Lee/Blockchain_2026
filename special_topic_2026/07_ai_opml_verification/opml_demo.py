"""
07_ai_opml_verification/opml_demo.py  (특강 2026-11-25)
=======================================================
AI 추론을 체인에서 어떻게 검증하나? — 전부 다시 계산하지 않고 '이분 탐색'과 '불시 검사'로

Part A. opML 방식(낙관적 검증 + 분쟁 시 이분 탐색)
  - 오프체인 VM 이 1,024 단계를 실행하고 단계별 상태 해시를 남긴다.
  - 제출자가 637단계에서 값을 속였다. 도전자가 이분 탐색으로 '처음 어긋난 한 단계'를 찾는다.
  - 체인(스마트 컨트랙트)은 그 한 단계만 직접 실행해 판정한다.
Part B. 확률적 표본 검사(Proof of Sampling 아이디어, 단순화)
  - 속이면 이득 G, 걸리면 벌금 S. 검사 확률 p 가 G/(G+S) 보다 크면 속이는 게 손해.

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/07_ai_opml_verification/opml_demo.py
  uv run python special_topic_2026/07_ai_opml_verification/opml_demo.py --web     # 브라우저 시각화
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)

※ 개념 시뮬레이션입니다. 실제 opML 은 MIPS VM 의 상태 Merkle root 로 이분 탐색하고, PoSP 는 스테이크·평판·중재 구조가 더 있습니다.
"""
import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (bad, bar, c, done, good, kv, line, live, live_end, open_web, pause,
                              say, sleep, step, title, wants_web)

N = 1024
CHEAT_AT = 637


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def step_fn(state: str, t: int) -> str:
    """VM 한 단계 (결정적 전이). 실제로는 행렬곱 등 연산 한 스텝에 해당"""
    return h(f"{state}|{t}|op{t % 7}".encode())


def run(init: str, cheat_from=None):
    s = [init]
    for t in range(N):
        nxt = step_fn(s[-1], t)
        if cheat_from is not None and t == cheat_from:
            nxt = h(b"forged" + nxt.encode())
        s.append(nxt)
    return s


def ruler(lo, hi, width=64):
    """1024 단계를 64칸으로 압축: 초록=합의된 구간, 노랑=아직 모르는 구간, 빨강=어긋난 구간"""
    per = N / width
    out = ""
    for i in range(width):
        a, b = i * per, (i + 1) * per
        if b <= lo:
            out += c("█", "green")
        elif a >= hi:
            out += c("█", "red")
        else:
            out += c("▒", "yellow")
    return out


def part_a():
    title("Part A. opML — 1,024 단계 추론, 조작을 이분 탐색으로 적발")
    say("상황: 누군가 'AI 추론 결과는 이것'이라고 체인에 올렸다. 맞는지 체인이 직접 1,024단계를 다시 계산하면 가스가 폭발한다.")

    step("A1. 오프체인 VM 이 추론을 실행한다 — 제출자와 도전자가 각자 계산해 단계별 상태 해시를 남긴다")
    say(f"제출자는 {CHEAT_AT}단계에서 값을 슬쩍 바꾸고(모델 교체·결과 조작), 그 값에서 계속 진행한다.")
    honest = run("input:cat.png")
    liar = run("input:cat.png", cheat_from=CHEAT_AT)
    for t in range(0, N + 1, 32):
        live(f"  실행 {t:>4}/{N}  {bar(t / N, 36)}  상태 {honest[t][:10]}…")
        sleep(0.04)
    live_end(f"  실행 {N}/{N}  {bar(1, 36)}  완료")
    print()
    print(c("   단계    제출자 상태 해시   도전자 상태 해시   비교", "dim"))
    for t in range(0, N + 1, 128):
        same = honest[t] == liar[t]
        line(f"  {t:>5}    {liar[t][:12]}…    {honest[t][:12]}…    "
             f"{c('일치', 'green') if same else c('불일치', 'red', 'bold')}", 0.25)
    say("512 까지는 같고 640 부터 다르다 → 어딘가에서 어긋났다. 정확히 어디일까?")

    step("A2. 최종 결과가 다르다 → 분쟁(dispute) 개시. 이제 '처음 어긋난 한 단계'를 찾는다")
    kv("제출자가 올린 결과", liar[-1][:20] + "…", width=18)
    kv("도전자가 계산한 결과", honest[-1][:20] + "…", width=18)
    bad("결과 불일치 → 도전 기간 안에 분쟁을 제기, 스테이크를 걸고 이분 탐색 시작")
    say("조건: 0단계는 둘이 같음(입력이 같으니까), 1024단계는 다름. → 그 사이 어딘가에 '처음 달라진 단계'가 있다.")

    step("A3. 이분 탐색 — 구간의 가운데 단계 상태 해시만 서로 비교한다")
    lo, hi, rounds = 0, N, 0
    print(f"  {c('█', 'green')}=합의됨  {c('▒', 'yellow')}=후보 구간  {c('█', 'red')}=어긋남   (1칸 = 16단계)")
    print(f"  시작    {ruler(lo, hi)}   [{lo}, {hi}]")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        rounds += 1
        pause(f"Enter ▶ 라운드 {rounds}")
        same = honest[mid] == liar[mid]
        print(f"  라운드 {rounds:>2}  중간 {mid:>4}단계  제출자 {liar[mid][:8]}…  도전자 {honest[mid][:8]}…  "
              f"→ {c('일치: 오른쪽 절반', 'green') if same else c('불일치: 왼쪽 절반', 'red')}")
        lo, hi = (mid, hi) if same else (lo, mid)
        print(f"          {ruler(lo, hi)}   [{lo}, {hi}]  후보 {hi - lo}단계")
    say(f"{rounds}번 비교로 후보가 1단계로 좁혀졌다 (log₂ {N} = {rounds}).")

    step(f"A4. 체인(스마트 컨트랙트)이 '그 한 단계'만 직접 실행해 판정한다  [{lo} → {hi}]")
    kv("합의된 입력 상태", f"s[{lo}] = {honest[lo][:16]}…  (두 사람이 이미 일치)", width=18)
    on_chain = step_fn(honest[lo], lo)
    kv("체인이 실행한 결과", f"s[{hi}] = {on_chain[:16]}…", width=18)
    kv("도전자의 주장", f"s[{hi}] = {honest[hi][:16]}…", width=18)
    kv("제출자의 주장", f"s[{hi}] = {liar[hi][:16]}…", width=18)
    ok_c, ok_l = on_chain == honest[hi], on_chain == liar[hi]
    (good if ok_c else bad)(f"도전자 일치: {ok_c}")
    (good if ok_l else bad)(f"제출자 일치: {ok_l}")
    print()
    print("  " + c("⇒ 제출자 패배 · 스테이크 몰수, 정답은 도전자의 계산 결과로 확정", "green", "bold"))
    kv("체인 비용", f"해시 비교 {rounds}번 + 1단계 실행   (직접 재계산: {N}단계)", width=10)
    kv("절감", f"약 {N / (rounds + 1):.0f}배", width=10)
    say("평소에는 아무도 이의를 제기하지 않으면 '낙관적으로' 결과가 확정된다 (optimistic).")


def part_b():
    title("Part B. 불시 검사 — 속이는 게 이득이 되는 검사 확률은?")
    G, S = 1.0, 20.0

    step("B1. 속이는 노드의 기대 손익을 식으로 쓴다")
    kv("G", f"{G}  : 속여서 아끼는 계산 비용(작업 1건당 이득)", width=4)
    kv("S", f"{S}  : 걸렸을 때 몰수되는 스테이크(벌금)", width=4)
    kv("p", "작업 1건이 무작위로 재검사될 확률", width=4)
    print()
    print("  속이는 노드의 기대이익  =  (1 − p) × G  −  p × S")
    pstar = G / (G + S)
    print(f"  손익분기 p* :  (1 − p)G = pS   →   p* = G / (G + S) = {G} / {G + S} = {c(f'{pstar:.4f}', 'yellow', 'bold')}")
    say("p 가 p* 보다 크면 속이는 쪽이 손해 → 정직하게 계산하는 편이 이득.")

    step("B2. 검사 확률에 따른 기대이익")
    print(c("        p   속임의 기대이익   (+이익 / −손해)", "dim"))
    for p in [0.00, 0.02, 0.04, pstar, 0.06, 0.10, 0.20]:
        ev = (1 - p) * G - p * S
        n = int(abs(ev) * 12)
        gauge = c("+" * n, "green") if ev >= 0 else c("-" * n, "red")
        tag = c("  ← p*", "yellow") if abs(p - pstar) < 1e-9 else ""
        line(f"  {p:>7.4f}   {ev:>10.3f}      {gauge}{tag}", 0.3)
    say("모든 작업을 재검사할 필요는 없다. p* 를 넘는 '불시 검사'만으로 속일 유인이 사라진다.")

    step("B3. 시뮬레이션 — 작업 10,000건, 속이는 노드의 누적 손익 (p=0.02 vs p=0.10)")
    say("적발되어도 계속 속인다고 가정한 단순 모델 (실제로는 적발 즉시 스테이크 몰수·퇴출).")
    random.seed(2026)
    probs = (0.02, 0.10)
    bal = {p: 0.0 for p in probs}
    first = {p: None for p in probs}
    for t in range(1, 10001):
        for p in probs:
            if random.random() < p:
                if first[p] is None:
                    first[p] = t
                bal[p] -= S
            else:
                bal[p] += G
        if t % 500 == 0:
            live("  " + "   ".join(f"p={p:.2f}: {bal[p]:>9,.0f}" for p in probs) + f"   ({t:,}/10,000건)")
            sleep(0.08)
    live_end("  " + "   ".join(f"p={p:.2f}: {bal[p]:>9,.0f}" for p in probs) + "   (10,000/10,000건)")
    for p in probs:
        verdict = c("속이는 쪽이 이득", "red") if bal[p] > 0 else c("속이는 쪽이 손해 ✔", "green")
        kv(f"p={p:.2f}", f"누적 {bal[p]:>9,.0f}  첫 적발 {first[p]}번째 작업  → {verdict}", width=7)
    say("p*(0.048) 보다 낮으면 속임수가 이득, 높으면 손해. 임계값이 설계의 핵심.")
    say("실제 PoSP 는 노드 평판·스테이크 비례 검사 확률, 분쟁 시 중재 라운드가 더 있다.")


def main():
    if wants_web():
        open_web(Path(__file__).with_name("opml_viz.html"))
        return
    part_a()
    part_b()
    done("정리: opML = '틀렸을 때만' 이분 탐색으로 한 단계를 증명 / PoSP = 불시 검사로 속일 유인을 없앰.")
    say("브라우저 시각화(이분 탐색 격자 + 손익 슬라이더): 같은 명령에 --web")


if __name__ == "__main__":
    main()
