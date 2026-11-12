"""
02_pow_mining/pow_demo.py  (특강 2026-11-25)
============================================
Proof of Work: '해시가 0 으로 시작하는 nonce 찾기' 와 '과거 블록을 고치려면 다시 캐야 한다'

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
  1) 해시는 예측할 수 없다: 같은 데이터에 nonce 만 바꿔 본다
  2) 채굴: nonce 를 올리며 해시가 실시간으로 바뀌는 모습 (난이도 1 -> 4, 선택 5)
  3) 난이도별 평균 시도 횟수 (한 자리 올릴 때마다 약 16배)
  4) 블록 3개를 이어 캔다 -> 첫 블록 변조 -> 한 블록씩 다시 캘 때마다 다음 블록이 깨지는 연쇄

실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/02_pow_mining/pow_demo.py
  uv run python special_topic_2026/02_pow_mining/pow_demo.py --max-diff 5   # 5자리까지(수 초)
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)
"""
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (ANIM, bad, bar, c, done, good, hl_prefix, kv, line, live, live_end,
                              pause, say, sleep, step, title)

MAX_DIFF = 4
if "--max-diff" in sys.argv:
    MAX_DIFF = int(sys.argv[sys.argv.index("--max-diff") + 1])


def bh(prev: str, data: str, nonce: int) -> str:
    return hashlib.sha256(f"{prev}|{data}|{nonce}".encode()).hexdigest()


def mine(prev, data, diff, show=False, label=""):
    """show=True 면 실시간으로 nonce 와 해시를 보여 준다"""
    target = "0" * diff
    nonce, t0, last = 0, time.perf_counter(), 0.0
    while True:
        hx = bh(prev, data, nonce)
        if show and ANIM:
            now = time.perf_counter()
            if now - last > 0.04:   # 화면 갱신은 약 25회/초
                last = now
                live(f"  {label}nonce {nonce:>9,}  {hl_prefix(hx[:28], diff)}…")
        if hx.startswith(target):
            return nonce, hx, time.perf_counter() - t0
        nonce += 1


def main():
    title("Proof of Work — 해시 퍼즐과 변조 비용")

    step("1. 해시는 예측할 수 없다: 데이터는 그대로, nonce 만 바꿔 본다")
    data = "Alice->Bob 1BTC"
    say(f'입력 = "이전해시 | {data} | nonce".  nonce 를 0, 1, 2 … 로 올리면?')
    for n in range(8):
        hx = bh("genesis", data, n)
        line(f"  nonce {n}  →  {hl_prefix(hx[:40], 4)}…", 0.35)
    say("전혀 규칙이 없다. 원하는 모양의 해시는 '계속 넣어 보는 수밖에' 없다.")

    step("2. 채굴: '해시가 0 으로 시작'할 때까지 nonce 를 올린다")
    for d in range(1, MAX_DIFF + 1):
        pause(f"Enter ▶ 난이도 {d} (앞자리 0 이 {d}개)") if d > 1 else None
        print(c(f"\n  목표: 앞 {d}자리가 모두 0   (확률 1/16^{d} = 1/{16 ** d:,})", "yellow"))
        nonce, hx, sec = mine("genesis", f"{data} #{d}", d, show=True, label=f"[난이도 {d}] ")
        live_end(f"  {c('발견!', 'green', 'bold')} nonce={nonce:,}  {hl_prefix(hx, d)}")
        kv("시도 횟수", f"{nonce + 1:,} 회   (기대값 16^{d} = {16 ** d:,})")
        kv("걸린 시간", f"{sec:.3f} 초")
    say("한 자리가 늘 때마다 약 16배 더 걸린다. 검증은? → 해시 한 번이면 끝 (아래 확인).")
    good(f"검증: SHA256 한 번 계산으로 확인 → {bh('genesis', f'{data} #{MAX_DIFF}', nonce)[:16]}… (앞 {MAX_DIFF}자리가 0)")

    step("3. 난이도별 평균 (운이 좋으면 한 번에 맞기도 해서 여러 번 평균)")
    print(f"  {'난이도':>4} {'평균 시도':>12} {'기대값 16^d':>13}  {'평균 시간(s)':>10}")
    tot_n = tot_t = 0
    for d in range(1, MAX_DIFF + 1):
        trials = 8 if d <= 3 else 4
        tries, secs = [], []
        for k in range(trials):
            live(f"  난이도 {d} 시행 {k + 1}/{trials}  {bar((k + 1) / trials, 20)}")
            nonce, hx, sec = mine("genesis", f"{data} #{d}-{k}", d)
            tries.append(nonce + 1)
            secs.append(sec)
        tot_n += sum(tries)
        tot_t += sum(secs)
        live_end(f"  {d:>4} {sum(tries) / trials:>12,.0f} {16 ** d:>13,}  {sum(secs) / trials:>10.3f}")
    if tot_t > 0.02:
        rate = tot_n / tot_t
        kv("이 컴퓨터 속도", f"약 {rate / 1e6:.2f} MH/s (파이썬)", color="cyan")
        kv("난이도 8 이면", f"평균 약 {16 ** 8 / rate / 60:.0f} 분")
        kv("난이도 10 이면", f"평균 약 {16 ** 10 / rate / 3600:.0f} 시간")
    say("실제 비트코인은 전용 장비(ASIC)로 초당 수백 EH(10^18) 해시를 계산한다.")

    step("4. 블록 3개를 이어서 캔다 (난이도 4)")
    diff = 4
    chain, prev = [], "0" * 64
    datas = ["B1: Alice->Bob 5", "B2: Bob->Carol 2", "B3: Carol->Dave 1"]
    for i, d in enumerate(datas):
        pause(f"Enter ▶ 블록 {i + 1} 채굴") if i else None
        nonce, hx, sec = mine(prev, d, diff, show=True, label=f"[블록 {i + 1}] ")
        live_end(f"  {c('블록 ' + str(i + 1) + ' 완성', 'green', 'bold')}  시도 {nonce + 1:,}회")
        chain.append({"data": d, "prev": prev, "nonce": nonce, "hash": hx})
        print(f"     ┌ prev : {prev[:20]}…\n     │ data : {d}\n     │ nonce: {nonce:,}\n"
              f"     └ hash : {hl_prefix(hx[:20], diff)}…")
        prev = hx
    say("각 블록은 이전 블록의 해시를 품고 있다 → 사슬(chain).")

    def check(c_):
        """블록별 검사 결과를 반환"""
        out, p = [], "0" * 64
        for k, b in enumerate(c_):
            link = b["prev"] == p
            recomputed = bh(b["prev"], b["data"], b["nonce"])
            self_ok = recomputed == b["hash"] and recomputed.startswith("0" * diff)
            out.append((k + 1, link, self_ok))
            p = b["hash"]
        return out

    def status_line(c_):
        parts = []
        for k, link, self_ok in check(c_):
            parts.append(f"블록{k} " + (c("✔", "green") if link and self_ok else c("✘", "red")))
        return "   ".join(parts)

    step("5. 공격자가 블록 1 의 금액을 5 → 500 으로 고친다")
    print(f"  원본: {chain[0]['data']}")
    chain[0]["data"] = "B1: Alice->Bob 500"
    print(f"  변조: {c(chain[0]['data'], 'red')}")
    pause("Enter ▶ 사슬 검증")
    for k, link, self_ok in check(chain):
        sleep(0.6)
        if link and self_ok:
            good(f"블록 {k}: 정상")
        else:
            bad(f"블록 {k}: 내용으로 다시 계산한 해시가 기록과 다름 (변조 탐지)")
    say("데이터를 바꾸면 그 블록의 해시가 달라진다. 해시를 새로 쓰려면 난이도 조건(앞자리 0)을 다시 맞춰야 한다 → 재채굴.")

    step("6. 공격자가 한 블록씩 다시 캐며 사슬을 고친다 — 고칠수록 다음 블록이 깨진다")
    prev, redo, total = "0" * 64, [dict(b) for b in chain], 0
    print("  시작 상태   " + status_line(redo))
    for k in range(len(redo)):
        pause(f"Enter ▶ 블록 {k + 1} 재채굴")
        b = redo[k]
        b["prev"] = prev
        nonce, hx, sec = mine(prev, b["data"], diff, show=True, label=f"[재채굴 블록 {k + 1}] ")
        live_end(f"  블록 {k + 1} 재채굴 완료  시도 {nonce + 1:,}회")
        b["nonce"], b["hash"] = nonce, hx
        total += nonce + 1
        prev = hx
        print("  현재 상태   " + status_line(redo))
        if k < len(redo) - 1:
            say(f"블록 {k + 1} 의 해시가 바뀌어서, 블록 {k + 2} 가 가리키는 이전 해시와 맞지 않는다.")
    ok = all(a and b for _, a, b in check(redo))
    (good if ok else bad)(f"재구성한 사슬 유효: {ok}   (총 {total:,}회 시도)")
    say("변조 하나가 '뒤의 모든 블록을 다시 캐는 일'이 된다. 그 사이 정직한 네트워크는 새 블록을 계속 붙인다.")
    say("변조 비용 ≈ (변조한 블록 뒤에 쌓인 블록 수) × 난이도.  '6 블록 확인' 관례의 이유.")
    say("※ 노트북 한 대는 시연일 뿐. 실제 공격은 네트워크 해시파워의 과반(51%)이 필요하다.")

    done("정리: PoW = 만들기는 어렵고(수없이 시도) 검증은 쉽다(한 번) → 과거를 고치는 비용이 곧 보안.")


if __name__ == "__main__":
    main()
