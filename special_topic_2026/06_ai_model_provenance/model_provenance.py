"""
06_ai_model_provenance/model_provenance.py  (특강 2026-11-25)
=============================================================
AI 모델 출처 증명: 가중치 파일을 조각내 Merkle root 로 서명하면, 한 비트 변조(백도어)도 잡힌다

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
  1) 모델 가중치 16조각을 만들고 조각마다 해시
  2) Merkle root 계산 -> 제공자가 ECDSA 서명 (레지스트리/체인에는 root 만 기록)
  3) 미러 사이트에서 받은 모델 검증: 정상
  4) 조각 9 의 1비트만 뒤집는다(백도어 삽입 가정) -> root 가 완전히 달라짐
  5) 어느 조각인지 root 에서 내려가며 4번 비교로 찾기
  6) 조각 1개 + 증명 경로(해시 4개)만으로 검증
  7) 파인튜닝 이력을 해시 체인으로 묶기

실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/06_ai_model_provenance/model_provenance.py
  uv run python special_topic_2026/06_ai_model_provenance/model_provenance.py --web   # 브라우저 시각화
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)

※ '가중치'는 시연용 난수 바이트입니다. 실제 모델 파일(.safetensors 등)도 같은 방식으로 조각 해시를 만들 수 있습니다.
"""
import base64
import hashlib
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (bad, c, done, good, kv, line, open_web, pause, say, sleep, step, title,
                              wants_web)

N_SHARDS, SHARD_BYTES = 16, 4096


def h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def s8(b: bytes) -> str:
    return b.hex()[:8]


def make_model(seed: str):
    shards = []
    for i in range(N_SHARDS):
        buf, ctr = b"", 0
        while len(buf) < SHARD_BYTES:
            buf += h(f"{seed}|{i}|{ctr}".encode())
            ctr += 1
        shards.append(buf[:SHARD_BYTES])
    return shards


def tree(shards):
    levels = [[h(s) for s in shards]]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        levels.append([h(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
    return levels


def proof(levels, idx):
    out = []
    for lv in levels[:-1]:
        out.append((lv[idx ^ 1], "R" if idx ^ 1 > idx else "L"))
        idx //= 2
    return out


def sign(priv, data: bytes) -> str:
    return base64.b64encode(priv.sign(data, ec.ECDSA(hashes.SHA256()))).decode()


def verify_sig(pub, data: bytes, sig: str) -> bool:
    try:
        pub.verify(base64.b64decode(sig), data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def main():
    if wants_web():
        open_web(Path(__file__).with_name("provenance_viz.html"))
        return

    title("AI 모델 출처 증명 — Merkle root + 서명")
    say("질문: 내가 내려받은 이 모델 파일이, 제공자가 공개한 바로 그 모델이 맞는가? (백도어는 없는가?)")
    provider = ec.generate_private_key(ec.SECP256R1())
    pub = provider.public_key()

    step("1. 모델 가중치(시연용 16조각 × 4,096바이트)를 조각내고, 조각마다 SHA-256 해시")
    shards = make_model("demo-llm-v1")
    lv = tree(shards)
    for i, s in enumerate(shards):
        line(f"  조각 {i:>2}  앞 8바이트 {s[:8].hex()}…   해시 {c(s8(lv[0][i]), 'cyan')}…", 0.15)
    say("실제 LLM 은 수 GB~수백 GB. 조각(shard)이 수천 개여도 같은 방식.")

    step("2. 해시를 Merkle 트리로 묶어 root 를 만들고, 제공자가 root 에 서명한다")
    for d in range(1, len(lv)):
        name = "root" if d == len(lv) - 1 else f"L{d}"
        row = " ".join(s8(x)[:6] for x in lv[d])
        line(f"  {name:<5} {row}", 0.5)
    root = lv[-1][0]
    sig = sign(provider, root)
    print()
    kv("Merkle root", c(root.hex(), "green", "bold"), width=14)
    kv("제공자 서명", c(sig[:36] + "…", "cyan"), width=14)
    (good if verify_sig(pub, root, sig) else bad)("제공자 공개키로 서명 검증 통과")
    say("레지스트리(또는 블록체인)에는 root 와 서명만 올린다. 모델 파일 자체는 올리지 않는다 (수십 GB).")

    step("3. 사용자가 미러 사이트에서 모델을 내려받아 root 를 다시 계산")
    got = tree(shards)
    kv("계산한 root", got[-1][0].hex()[:40] + "…", width=14)
    kv("공개된 root", root.hex()[:40] + "…", width=14)
    good("일치 → 제공자가 공개한 모델 그대로")

    step("4. 미러 운영자가 조각 9 에서 '딱 1비트'만 뒤집는다 (백도어 삽입 가정)")
    evil = [bytearray(s) for s in shards]
    pos, bit = 1234, 0
    before = evil[9][pos]
    evil[9][pos] ^= 1 << bit
    after = evil[9][pos]
    evil = [bytes(s) for s in evil]
    kv("변조 위치", f"조각 9 의 {pos}번째 바이트, {bit}번 비트", width=14)
    kv("바이트 값", f"{before:08b} → {c(f'{after:08b}', 'red', 'bold')}", width=14)
    kv("파일 크기", f"{N_SHARDS * SHARD_BYTES:,} 바이트 중 1비트 (= {1 / (N_SHARDS * SHARD_BYTES * 8):.6%})", width=14)
    lv_evil = tree(evil)
    pause("Enter ▶ 해시 다시 계산")
    kv("조각 9 해시", f"{s8(lv[0][9])}… → {c(s8(lv_evil[0][9]), 'red', 'bold')}…", width=14)
    for d in range(1, len(lv)):
        sleep(0.4)
        idx = 9 >> d
        name = "root" if d == len(lv) - 1 else f"L{d}"
        kv(f"{name} 해시", f"{s8(lv[d][idx])}… → {c(s8(lv_evil[d][idx]), 'red', 'bold')}…", width=14)
    print()
    bad(f"새 root {lv_evil[-1][0].hex()[:24]}…  ≠  공개된 root {root.hex()[:24]}…  → 사용 금지")
    say("눈에 보이지도 않는 1비트가, 해시를 타고 올라가 root 를 완전히 바꾼다 (눈사태 효과).")

    step("5. 어느 조각이 바뀌었나? root 에서 아래로 내려가며 '다른 쪽'만 따라간다")
    idx, cmp_n = 0, 0
    for d in range(len(lv) - 1, 0, -1):
        left = idx * 2
        cmp_n += 1
        same_left = lv[d - 1][left] == lv_evil[d - 1][left]
        nxt = left + 1 if same_left else left
        line(f"  레벨 {d} → {d - 1}:  왼쪽 자식 {s8(lv[d - 1][left])} vs {s8(lv_evil[d - 1][left])}  "
             f"{'같음 → 오른쪽으로' if same_left else c('다름 → 왼쪽으로', 'red')}", 0.7)
        idx = nxt
    good(f"변조된 조각 = #{idx}   (비교 {cmp_n}회 = log₂ {N_SHARDS})")
    say(f"하나씩 모두 비교하면 {N_SHARDS}번. 조각이 100만 개여도 20번이면 찾는다 (opML 이분 탐색과 같은 원리).")

    step("6. 모델 전체가 아니라 '조각 3 하나'만 받아서 검증 (증명 경로)")
    pf = proof(lv, 3)
    cur = h(shards[3])
    print(f"  받는 데이터: 조각 3 ({SHARD_BYTES:,}B) + 해시 {len(pf)}개")
    print(f"  시작: H(조각 3) = {s8(cur)}")
    for k, (sib, side) in enumerate(pf, 1):
        cur = h(cur + sib) if side == "R" else h(sib + cur)
        line(f"  {k}) 형제({side}) {s8(sib)} 와 결합 → {s8(cur)}", 0.6)
    (good if cur == root else bad)(f"계산한 root {s8(cur)}…  {'==' if cur == root else '≠'}  공개된 root {s8(root)}…")
    cur = h(evil[9])
    for sib, side in proof(lv, 9):
        cur = h(cur + sib) if side == "R" else h(sib + cur)
    (good if cur == root else bad)(f"변조된 조각 9 로 검증하면: root {s8(cur)}…  → {'통과' if cur == root else '실패 (변조 탐지)'}")

    step("7. 파인튜닝 이력: 체크포인트 ID = H(이전 ID ‖ 이번 root) — 해시 체인")
    hist, prev = [], b"\x00" * 32
    for name in ["base", "finetune-A", "finetune-B"]:
        r = tree(make_model(name))[-1][0]
        rec = h(prev + r)
        hist.append((name, r, rec))
        line(f"  {name:<11} root {s8(r)}…   체크포인트 ID {c(s8(rec), 'cyan')}…  (이전 {s8(prev)}…)", 0.6)
        prev = rec
    fake_base = tree(make_model("base-backdoored"))[-1][0]
    p2 = h(b"\x00" * 32 + fake_base)
    for _, r, _ in hist[1:]:
        p2 = h(p2 + r)
    print()
    bad(f"base 를 몰래 교체하면 최종 ID 가 {s8(hist[-1][2])}… → {c(s8(p2), 'red')}…  (이력 위조 즉시 탐지)")

    done("정리: 제공자 서명 + root 공개 = '이 모델이 그 모델이다'를 누구나 검증. 블록체인은 root 를 위조 불가능하게 게시하는 곳.")
    say("한계: 모델이 좋은지·안전한지는 증명하지 않는다. 변조 여부와 출처만 증명한다.")
    say("브라우저 시각화: 같은 명령에 --web")


if __name__ == "__main__":
    main()
