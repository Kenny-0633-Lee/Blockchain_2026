"""
01_merkle_tamper/merkle_tamper.py  (특강 2026-11-25)
====================================================
Merkle Tree: 한 글자만 바뀌어도 루트가 바뀐다 / 증명 경로는 log2(n) 개 해시

보여줄 것
  1) 거래 16개 -> Merkle root
  2) 거래 하나를 변조하면 루트까지 어떤 노드가 바뀌는가 (표시: *)
  3) 포함 증명(Merkle proof): 16개 중 1개를 4개 해시만으로 검증
  4) 거래가 6만 개여도 증명은 16개 해시

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통, 저장소 루트에서)
  uv run python special_topic_2026/01_merkle_tamper/merkle_tamper.py
  (uv 가 없으면: python special_topic_2026/01_merkle_tamper/merkle_tamper.py  - 표준 라이브러리만 사용)
"""
import hashlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def build(leaves):
    """levels[0]=잎, levels[-1]=[root]. 홀수면 마지막 노드 복제(Bitcoin 방식)"""
    levels = [[h(x.encode()) for x in leaves]]
    while len(levels[-1]) > 1:
        cur = levels[-1][:]
        if len(cur) % 2:
            cur.append(cur[-1])
        levels.append([h((cur[i] + cur[i + 1]).encode()) for i in range(0, len(cur), 2)])
    return levels


def proof(levels, idx):
    out = []
    for lv in levels[:-1]:
        lv = lv + [lv[-1]] if len(lv) % 2 else lv
        sib = idx ^ 1
        out.append((lv[sib], "R" if sib > idx else "L"))
        idx //= 2
    return out


def verify(leaf_text, pf, root):
    cur = h(leaf_text.encode())
    for sib, side in pf:
        cur = h((cur + sib).encode()) if side == "R" else h((sib + cur).encode())
    return cur == root


def show(levels, marks=None, title=""):
    print(title)
    for d in range(len(levels) - 1, -1, -1):
        row = []
        for i, x in enumerate(levels[d]):
            m = "*" if marks and x != marks[d][i] else " "
            row.append(f"{x[:6]}{m}")
        print(f"  L{d} " + " ".join(row))


def main():
    txs = [f"tx{i:02d}: 사용자{i} -> 사용자{(i * 7) % 16} : {10 + i} coin" for i in range(16)]
    lv = build(txs)
    print("[1] 거래 16개의 Merkle tree (각 노드 해시 앞 6자리)")
    show(lv)
    print(f"  Merkle root = {lv[-1][0]}")

    print("\n[2] tx05 의 금액을 15 -> 1500 으로 변조 (바뀐 노드에 * 표시)")
    bad = txs[:]
    bad[5] = bad[5].replace("15 coin", "1500 coin")
    lv2 = build(bad)
    show(lv2, marks=lv, title="  변조 후 트리:")
    print(f"  새 root     = {lv2[-1][0]}")
    changed = sum(1 for d in range(len(lv)) for i in range(len(lv[d])) if lv[d][i] != lv2[d][i])
    print(f"  바뀐 노드 {changed}개 / 전체 {sum(len(x) for x in lv)}개  -> 잎에서 루트까지 한 줄로 번진다.")
    print("  블록 헤더에는 root 만 있으므로, 헤더를 바꾸지 않는 한 거래 변조는 즉시 들통난다.")

    print("\n[3] 포함 증명: 'tx05 는 이 root 에 포함된다' 를 해시 4개로 확인")
    pf = proof(lv, 5)
    for k, (s, side) in enumerate(pf):
        print(f"  증명 {k + 1}: 형제({side}) {s[:12]}…")
    print(f"  원본 tx05  검증: {verify(txs[5], pf, lv[-1][0])}")
    print(f"  변조 tx05  검증: {verify(bad[5], pf, lv[-1][0])}")

    print("\n[4] 규모를 키우면?")
    n = 2 ** 16
    big = build([f"tx{i}" for i in range(n)])
    pf_big = proof(big, 12345)
    print(f"  거래 {n:,}개 -> 증명 길이 {len(pf_big)}개 해시 (=log2 n), 전체를 받을 필요 없음")
    print(f"  검증: {verify('tx12345', pf_big, big[-1][0])}")
    print("  => 스마트폰(SPV 지갑)이 블록 전체 없이 '내 거래가 들어갔다'를 확인하는 원리")


if __name__ == "__main__":
    main()
