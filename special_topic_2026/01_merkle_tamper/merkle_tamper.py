"""
01_merkle_tamper/merkle_tamper.py  (특강 2026-11-25)
====================================================
Merkle Tree: 한 글자만 바뀌어도 루트가 바뀐다 / 증명 경로는 log2(n) 개 해시

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
  1) 거래 16개를 하나씩 해시 -> 잎(leaf)
  2) 두 개씩 묶어 부모 해시를 만들며 루트까지 올라간다 (계산식이 보인다)
  3) tx05 금액 변조 -> 바뀐 노드만 추적 (잎에서 루트까지 한 줄)
  4) 포함 증명: 형제 해시 4개로 루트를 다시 만들어 본다
  5) 거래 65,536개여도 증명은 16개

실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/01_merkle_tamper/merkle_tamper.py
  uv run python special_topic_2026/01_merkle_tamper/merkle_tamper.py --web    # 브라우저 시각화
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (bad, c, done, good, kv, line, live, live_end, open_web, pause,
                              say, sleep, step, title, wants_web)


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def s6(x):
    return x[:6]


def build(leaves):
    levels = [[h(x) for x in leaves]]
    while len(levels[-1]) > 1:
        cur = levels[-1][:]
        if len(cur) % 2:
            cur.append(cur[-1])
        levels.append([h(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
    return levels


def proof(levels, idx):
    out = []
    for lv in levels[:-1]:
        lv = lv + [lv[-1]] if len(lv) % 2 else lv
        sib = idx ^ 1
        out.append((lv[sib], "R" if sib > idx else "L"))
        idx //= 2
    return out


def tree_text(levels, marks=None):
    for d in range(len(levels) - 1, -1, -1):
        cells = []
        for i, x in enumerate(levels[d]):
            diff = marks is not None and x != marks[d][i]
            cells.append(c(f"{s6(x)}*", "red", "bold") if diff else f"{s6(x)} ")
        print(c(f"  L{d} ", "dim") + " ".join(cells))


def main():
    if wants_web():
        open_web(Path(__file__).with_name("merkle_viz.html"))
        return

    title("Merkle Tree — 변조가 루트까지 번지는 모습")
    txs = [f"tx{i:02d}: 사용자{i} -> 사용자{(i * 7) % 16} : {10 + i} coin" for i in range(16)]

    step("1. 거래 16개를 하나씩 해시한다 (잎 = leaf)")
    say("해시는 거래 내용의 '지문'. 내용이 같으면 같은 값, 한 글자만 달라도 완전히 다른 값.")
    lv = build(txs)
    for i, t in enumerate(txs):
        line(f"  {t}   {c('→', 'dim')} {c(s6(lv[0][i]), 'cyan')}…", 0.12)

    step("2. 두 개씩 묶어 부모 해시를 만든다:  부모 = SHA256( 왼쪽해시 ‖ 오른쪽해시 )")
    for d in range(1, len(lv)):
        name = "루트(root)" if d == len(lv) - 1 else f"L{d}"
        print(c(f"\n  ── {name} ──", "yellow"))
        for i, x in enumerate(lv[d]):
            a, b = lv[d - 1][2 * i], lv[d - 1][2 * i + 1]
            line(f"  H({s6(a)} ‖ {s6(b)}) = {c(s6(x), 'cyan')}", 0.10)
        if d < len(lv) - 1:
            pause(f"Enter ▶ L{d + 1} 로 올라가기")
    print()
    print(c("  Merkle root = ", "dim") + c(lv[-1][0], "green", "bold"))
    say("블록 헤더에는 이 값 하나만 들어간다. 거래 16개 전체가 이 한 줄에 '묶여' 있다.")
    print()
    tree_text(lv)

    step("3. tx05 의 금액을 15 → 1500 으로 변조해 보자")
    bad_txs = txs[:]
    bad_txs[5] = bad_txs[5].replace("15 coin", "1500 coin")
    print(f"  원본: {txs[5]}")
    print(f"  변조: {c(bad_txs[5], 'red')}")
    lv2 = build(bad_txs)
    pause("Enter ▶ 바뀐 해시 추적")
    idx = 5
    print(c(f"\n  L0  tx05 해시   {s6(lv[0][5])} → {c(s6(lv2[0][5]), 'red', 'bold')}"))
    for d in range(1, len(lv)):
        idx //= 2
        sleep(0.5)
        print(f"  L{d}  {('루트    ' if d == len(lv) - 1 else '부모 해시')}   "
              f"{s6(lv[d][idx])} → {c(s6(lv2[d][idx]), 'red', 'bold')}")
    print()
    tree_text(lv2, marks=lv)
    changed = sum(1 for d in range(len(lv)) for i in range(len(lv[d])) if lv[d][i] != lv2[d][i])
    total = sum(len(x) for x in lv)
    print(f"\n  바뀐 노드 {c(changed, 'red', 'bold')}개 / 전체 {total}개  → 잎에서 루트까지 한 줄로 번진다.")
    bad(f"새 root = {lv2[-1][0][:24]}…  ≠  원래 root {lv[-1][0][:24]}…")
    say("헤더의 root 를 몰래 바꾸지 않는 한, 거래 변조는 즉시 들통난다.")

    step("4. 포함 증명(Merkle proof): '내 거래 tx05 가 이 root 안에 있다'를 4개 해시로 확인")
    say("받는 것: 내 거래 + 형제 해시 4개.  블록의 나머지 거래는 필요 없다.")
    pf = proof(lv, 5)
    for label, text in (("원본 tx05", txs[5]), ("변조 tx05", bad_txs[5])):
        print(c(f"\n  [{label}]  {text}", "bold"))
        cur = h(text)
        print(f"    시작: H(거래) = {s6(cur)}")
        for k, (sib, side) in enumerate(pf, 1):
            nxt = h(cur + sib) if side == "R" else h(sib + cur)
            form = f"H({s6(cur)} ‖ {s6(sib)})" if side == "R" else f"H({s6(sib)} ‖ {s6(cur)})"
            sleep(0.6)
            print(f"    {k}) 형제({side}) {s6(sib)}  →  {form} = {s6(nxt)}")
            cur = nxt
        ok = cur == lv[-1][0]
        (good if ok else bad)(f"계산한 root {s6(cur)}  {'==' if ok else '≠'}  블록의 root {s6(lv[-1][0])}"
                              f"   → {'포함 확인' if ok else '검증 실패 (변조됨)'}")
        pause("Enter ▶ 계속")

    step("5. 거래가 65,536개라면?")
    n = 2 ** 16
    live("  트리 구성 중…")
    big = build([f"tx{i}" for i in range(n)])
    live_end(f"  거래 {n:,}개의 트리 완성   root = {s6(big[-1][0])}…")
    pf_big = proof(big, 12345)
    kv("증명 길이", f"{len(pf_big)}개 해시 (= log₂ {n:,})", color="green")
    kv("전체 대비", f"{len(pf_big)} / {n:,} = {len(pf_big) / n:.4%}")
    cur = h("tx12345")
    for sib, side in pf_big:
        cur = h(cur + sib) if side == "R" else h(sib + cur)
    (good if cur == big[-1][0] else bad)("증명 검증 " + ("성공" if cur == big[-1][0] else "실패"))
    say("스마트폰 지갑(SPV)이 블록 전체 없이 '내 거래가 들어갔다'를 확인하는 원리.")

    done("정리: 해시 하나(root)가 거래 전체를 지킨다 — 변조는 잎에서 루트까지 번지고, 증명은 log n.")
    say("브라우저 시각화: 같은 명령에 --web")


if __name__ == "__main__":
    main()
