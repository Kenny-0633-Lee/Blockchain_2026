"""
06_ai_model_provenance/model_provenance.py  (특강 2026-11-25)
=============================================================
AI 모델 출처 증명: 가중치 파일을 조각내 Merkle root 로 서명하면, 한 바이트 변조(백도어)도 잡힌다

보여줄 것
  1) 모델 가중치 16조각 -> Merkle root -> 제공자가 ECDSA 서명 (원장/레지스트리에는 root 만 기록)
  2) 미러 사이트에서 받은 모델 검증: 정상 / 한 바이트 변조
  3) 어느 조각이 바뀌었는지 root 에서 아래로 내려가며 log n 번 비교로 찾기
  4) 조각 하나만 받아 증명 경로(4개 해시)로 검증 (전체 다운로드 불필요)
  5) 파인튜닝 이력: 체크포인트가 이전 root 를 해시로 물고 있어 이력 조작을 막는다

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통, 저장소 루트에서)
  uv run python special_topic_2026/06_ai_model_provenance/model_provenance.py

※ '가중치'는 시연용 난수 바이트입니다. 실제 모델 파일(.safetensors 등)도 같은 방식으로 조각 해시를 만들 수 있습니다.
"""
import base64
import hashlib
import sys

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N_SHARDS, SHARD_BYTES = 16, 4096


def h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def make_model(seed: str):
    """결정적 난수 바이트 16조각 (시연 재현용)"""
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
    return levels  # 16 = 2^4 이므로 복제 불필요


def proof(levels, idx):
    out = []
    for lv in levels[:-1]:
        out.append((lv[idx ^ 1], "R" if idx ^ 1 > idx else "L"))
        idx //= 2
    return out


def verify_shard(shard, pf, root):
    cur = h(shard)
    for sib, side in pf:
        cur = h(cur + sib) if side == "R" else h(sib + cur)
    return cur == root


def locate(a, b):
    """두 트리의 root 가 다를 때, 위에서 아래로 다른 쪽 자식만 따라 내려간다. (비교 횟수 반환)"""
    idx, cmp = 0, 0
    for d in range(len(a) - 1, 0, -1):
        left = idx * 2
        cmp += 1
        idx = left if a[d - 1][left] != b[d - 1][left] else left + 1
    return idx, cmp


def sign(priv, data: bytes) -> str:
    return base64.b64encode(priv.sign(data, ec.ECDSA(hashes.SHA256()))).decode()


def verify_sig(pub, data: bytes, sig: str) -> bool:
    try:
        pub.verify(base64.b64decode(sig), data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def main():
    provider = ec.generate_private_key(ec.SECP256R1())
    pub = provider.public_key()

    print("[1] 모델 제공자: 16조각 -> Merkle root -> 서명 (이 root 만 공개 레지스트리/체인에 기록)")
    shards = make_model("demo-llm-v1")
    lv = tree(shards)
    root = lv[-1][0]
    sig = sign(provider, root)
    print(f"  모델 크기(시연): {N_SHARDS} x {SHARD_BYTES}B   root = {root.hex()[:32]}…")
    print(f"  제공자 서명: {sig[:28]}…  검증: {verify_sig(pub, root, sig)}")

    print("\n[2] 사용자가 미러에서 내려받아 검증")
    got = tree(shards)
    print(f"  정상 파일  : root 일치 = {got[-1][0] == root}")
    evil = [bytearray(s) for s in shards]
    evil[9][1234] ^= 0x01  # 조각 9의 한 비트만 뒤집음 (백도어 삽입 가정)
    evil = [bytes(s) for s in evil]
    lv_evil = tree(evil)
    print(f"  1비트 변조 : root 일치 = {lv_evil[-1][0] == root}   (새 root = {lv_evil[-1][0].hex()[:16]}…)")
    print("  -> 모델 전체 {:,} 바이트 중 1비트가 달라졌을 뿐인데 root 가 완전히 바뀐다.".format(N_SHARDS * SHARD_BYTES))

    print("\n[3] 어느 조각이 바뀌었나? root 에서 내려가며 비교")
    idx, cmp = locate(lv, lv_evil)
    print(f"  찾은 조각: #{idx}  (실제 변조 조각: #9)   비교 횟수 {cmp}회 (=log2 {N_SHARDS})")
    print(f"  전체를 하나씩 비교하면 {N_SHARDS}회. 조각이 100만 개여도 20회.")

    print("\n[4] 조각 #3 만 받아서 검증 (증명 경로)")
    pf = proof(lv, 3)
    print(f"  받는 데이터: 조각 1개 + 해시 {len(pf)}개   검증: {verify_shard(shards[3], pf, root)}")
    print(f"  변조 조각 검증: {verify_shard(evil[9], proof(lv, 9), root)}")

    print("\n[5] 파인튜닝 이력: 체크포인트가 이전 root 를 물고 있다 (해시 체인)")
    hist, prev = [], b"\x00" * 32
    for name in ["base", "finetune-A", "finetune-B"]:
        sh = make_model(name)
        r = tree(sh)[-1][0]
        rec = h(prev + r)  # 체크포인트 ID = H(이전 ID || 이번 root)
        hist.append((name, r, prev, rec))
        print(f"  {name:<11} root={r.hex()[:10]}…  체크포인트 ID={rec.hex()[:10]}…")
        prev = rec
    # base 의 root 를 바꾸면(= 이력 조작) 뒤의 ID 가 모두 달라진다
    fake_base = tree(make_model("base-backdoored"))[-1][0]
    p2 = h(b"\x00" * 32 + fake_base)
    for name, r, _, _ in hist[1:]:
        p2 = h(p2 + r)
    print(f"  base 를 몰래 교체하면 최종 ID 가 {hist[-1][3].hex()[:10]}… -> {p2.hex()[:10]}…  (이력 위조 즉시 탐지)")

    print("\n정리: 제공자 서명 + root 공개 = '이 모델이 그 모델이다'를 누구나 검증. 블록체인은 root 를 위조 불가능하게 게시하는 곳.")
    print("한계: 모델이 '좋은지/안전한지'는 증명하지 않는다. 변조 여부와 출처만 증명한다.")


if __name__ == "__main__":
    main()
