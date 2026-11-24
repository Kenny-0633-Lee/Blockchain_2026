"""
07_ai_content_provenance/provenance_demo.py  (특강 2026-11-25)
=============================================================
딥페이크 시대의 '출처 증명' — 이 사진은 누가, 언제, 어떻게 만들었나? (C2PA 방식의 핵심 원리)

핵심 아이디어: '가짜를 찾아내는' 대신 '진짜에 서명을 남긴다'.
  1) 촬영 기기가 사진 해시 + 작성자 + 동작을 담은 '매니페스트'에 디지털 서명한다.
  2) 편집할 때마다 새 매니페스트가 이전 매니페스트의 해시를 가리킨다 (편집 이력 해시 체인).
  3) 검증자는 [해시 일치] [서명 유효] [신뢰 목록의 키] [이력 체인]을 확인한다.
  4) 매니페스트 해시를 블록체인에 기록하면 '그 시각에 이미 존재했음'을 누구나 확인한다.

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/07_ai_content_provenance/provenance_demo.py
  uv run python special_topic_2026/07_ai_content_provenance/provenance_demo.py --web     # 브라우저 시각화
옵션: --auto(멈춤 없이) --fast(애니메이션 없이) --no-art(터미널 그림 생략)

※ 개념 시뮬레이션입니다. 표준 라이브러리만 사용 (ECDSA P-256 을 직접 구현, 실제 서비스는 검증된 라이브러리 사용).
   서명 난수 k 를 해시에서 결정적으로 만들어 재현 가능하게 했습니다 (교육용).
   실제 C2PA 는 JUMBF/COSE 형식, X.509 인증서 체인, 신뢰 목록(Trust List)을 씁니다.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (COLOR, bad, c, done, good, kv, line, open_web, say, sleep, step,
                              title, wants_web)

# ───────────────────────── ECDSA P-256 (교육용 최소 구현) ─────────────────────────
P = 2**256 - 2**224 + 2**192 + 2**96 - 1
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
A = P - 3
G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
     0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        m = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        m = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (m * m - x1 - x2) % P
    return (x3, (m * (x1 - x3) - y1) % P)


def _mul(k, pt):
    r = None
    while k:
        if k & 1:
            r = _add(r, pt)
        pt = _add(pt, pt)
        k >>= 1
    return r


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Key:
    def __init__(self, name, seed):
        self.name = name
        self.d = int(sha(seed.encode()), 16) % (N - 1) + 1
        self.pub = _mul(self.d, G)

    @property
    def kid(self):  # 공개키 지문(짧게)
        return sha(f"{self.pub[0]:x}{self.pub[1]:x}".encode())[:12]

    def sign(self, msg_hash_hex):
        z = int(msg_hash_hex, 16)
        k = int(sha(f"{self.d}|{msg_hash_hex}".encode()), 16) % (N - 1) + 1
        r = _mul(k, G)[0] % N
        s = pow(k, -1, N) * (z + r * self.d) % N
        return (r, s)


def ecdsa_verify(pub, msg_hash_hex, sig):
    r, s = sig
    if not (0 < r < N and 0 < s < N):
        return False
    z, w = int(msg_hash_hex, 16), pow(s, -1, N)
    pt = _add(_mul(z * w % N, G), _mul(r * w % N, pub))
    return pt is not None and pt[0] % N == r


# ───────────────────────── 가상의 사진 (32×20 픽셀) ─────────────────────────
W, H = 32, 20


def make_photo(variant="real"):
    px = []
    for y in range(H):
        for x in range(W):
            if variant == "real":
                sun = (x - 22) ** 2 + (y - 5) ** 2 <= 9
                if sun:
                    col = (255, 214, 90)
                elif y < 11 - (3 if 6 < x < 15 else 0) - (2 if x > 24 else 0):
                    col = (90 + y * 6, 140 + y * 5, 230 - y * 3)
                elif y < 14:
                    col = (60, 110 + (x % 3) * 8, 70)
                else:
                    col = (40, 90 + (y - 14) * 12, 170)
            else:  # 딥페이크: 눈으로는 그럴듯하지만 전혀 다른 장면
                sun = (x - 8) ** 2 + (y - 6) ** 2 <= 14
                if sun:
                    col = (255, 90, 70)
                elif y < 12:
                    col = (200 - y * 6, 90 + y * 4, 120 + y * 5)
                else:
                    col = (70, 60 + (x % 4) * 10, 90)
            px.append(tuple(max(0, min(255, v)) for v in col))
    return px


def to_bytes(px):
    return bytes(v for p in px for v in p)


def brighten(px, d=24):
    return [tuple(min(255, v + d) for v in p) for p in px]


def flip_one_pixel(px, idx=11 * W + 20):
    px = list(px)
    r, g, b = px[idx]
    px[idx] = (r, g, b ^ 1)  # 파란 값의 마지막 비트 하나만 뒤집기
    return px


def art(px, label):
    """터미널용 작은 그림 (반 블록 문자). --no-art 이거나 색이 없으면 생략."""
    if not COLOR or "--no-art" in sys.argv:
        return
    print(f"  {c(label, 'dim')}")
    for y in range(0, H, 2):
        row = ""
        for x in range(W):
            t, b = px[y * W + x], px[(y + 1) * W + x]
            row += f"\033[38;2;{t[0]};{t[1]};{t[2]}m\033[48;2;{b[0]};{b[1]};{b[2]}m▀"
        print("   " + row + "\033[0m")


# ───────────────────────── 매니페스트 · 검증 ─────────────────────────
def canon(m):
    return json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def mhash(m):
    return sha(canon(m).encode())


def make_manifest(key, asset, creator, action, parent=None):
    m = {"asset_sha256": sha(asset), "creator": creator, "action": action,
         "parent": parent, "signer": key.kid}
    return {"m": m, "sig": key.sign(mhash(m)), "pub": key.pub}


def verify(asset, pkg, trust, store):
    """검증 항목 4가지를 돌려준다. 반환: (결과 목록, 최종 판정)"""
    if pkg is None:
        return [], ("none", "출처 없음 (서명 정보 없음)")
    m, res = pkg["m"], []
    res.append(("사진 해시 = 매니페스트의 해시", sha(asset) == m["asset_sha256"]))
    res.append(("서명 유효 (공개키로 검증)", ecdsa_verify(pkg["pub"], mhash(m), pkg["sig"])))
    res.append(("서명자가 신뢰 목록에 있음", m["signer"] in trust))
    ok_chain, p = True, m["parent"]
    while p:
        prev = store.get(p)
        if prev is None or not ecdsa_verify(prev["pub"], mhash(prev["m"]), prev["sig"]) \
                or prev["m"]["signer"] not in trust:
            ok_chain = False
            break
        p = prev["m"]["parent"]
    res.append(("편집 이력 체인이 끊기지 않음", ok_chain))
    if all(ok for _, ok in res):
        if m["action"].startswith("ai-generated"):
            return res, ("ai", "검증됨 · 'AI 생성' 표시")
        return res, ("ok", "검증됨 · 출처 확인")
    return res, ("fail", "검증 실패")


def show(res, verdict):
    for name, ok in res:
        (good if ok else bad)(name)
    kind, text = verdict
    mark = {"ok": c("● " + text, "green", "bold"), "ai": c("● " + text, "cyan", "bold"),
            "fail": c("● " + text, "red", "bold"), "none": c("● " + text, "yellow", "bold")}[kind]
    print(f"  판정: {mark}")


def short(h, n=16):
    return h[:n] + "…"


# ───────────────────────── 블록체인 앵커링 (아주 작은 장부) ─────────────────────────
class Ledger:
    def __init__(self):
        self.blocks = [{"h": 0, "prev": "0" * 64, "txs": ["genesis"]}]

    @staticmethod
    def bhash(b):
        return sha(f"{b['h']}|{b['prev']}|{','.join(b['txs'])}".encode())

    def add(self, txs):
        prev = self.bhash(self.blocks[-1])
        self.blocks.append({"h": len(self.blocks), "prev": prev, "txs": list(txs)})
        return self.blocks[-1]

    def find(self, x):
        for b in self.blocks:
            if x in b["txs"]:
                return b
        return None


# ───────────────────────── 시연 ─────────────────────────
def main():
    if wants_web():
        open_web(Path(__file__).with_name("provenance_viz.html"))
        return

    title("시연 ⑦  딥페이크 시대의 출처 증명 — 서명 · 해시 체인 · 블록체인 앵커")
    say("목표: '가짜 탐지'가 아니라 '진짜 증명'. 도구는 앞에서 본 해시 · 서명 · 블록체인 그대로.")

    # 1 ── 키와 신뢰 목록
    step("1) 참여자와 신뢰 목록 — 누구의 서명을 믿을 것인가")
    cam = Key("보도사진 카메라 (Leica형)", "camera-secret")
    desk = Key("편집부 데스크", "desk-secret")
    gen = Key("정직한 AI 생성 도구", "aigen-secret")
    evil = Key("공격자", "attacker-secret")
    for k in (cam, desk, gen, evil):
        kv(k.name, f"공개키 지문 {k.kid}")
    trust = {cam.kid, desk.kid, gen.kid}
    say("신뢰 목록(Trust List)에는 카메라·편집부·AI 도구만 있다. 공격자의 키는 없다.")
    say("실제 C2PA: 카메라·SW 제조사가 인증서를 받고, 검증 앱이 신뢰 목록으로 확인한다.")

    store, ledger = {}, Ledger()

    # 2 ── 촬영
    step("2) 촬영 — 사진 해시를 담은 매니페스트에 카메라가 서명")
    photo = make_photo("real")
    pa = to_bytes(photo)
    p0 = make_manifest(cam, pa, "김기자 · 서울", "captured")
    h0 = mhash(p0["m"])
    store[h0] = p0
    art(photo, "촬영 원본")
    kv("사진 해시", short(sha(pa), 32))
    kv("매니페스트", canon(p0["m"])[:76] + "…")
    kv("서명 (r)", short(f"{p0['sig'][0]:x}", 32))
    res, vd = verify(pa, p0, trust, store)
    show(res, vd)

    # 3 ── 편집 이력
    step("3) 편집 — 밝기 보정. 새 매니페스트가 '이전 매니페스트의 해시'를 가리킨다")
    ph1 = brighten(photo)
    pb = to_bytes(ph1)
    p1 = make_manifest(desk, pb, "편집부 데스크", "edited:brightness+24", parent=h0)
    h1 = mhash(p1["m"])
    store[h1] = p1
    art(ph1, "편집본 (밝기 +24)")
    kv("이력", f"{short(h0, 10)} (촬영) ← {short(h1, 10)} (편집)")
    res, vd = verify(pb, p1, trust, store)
    show(res, vd)
    say("편집은 허용된다. 다만 '누가 무엇을 했는지'가 이력으로 남는다. 해시 체인 — 블록체인과 같은 구조.")

    # 4 ── 공격 A
    step("4) 공격 A — 편집본에서 딱 1픽셀(파란 값의 비트 하나)만 바꾼다")
    tp = flip_one_pixel(ph1)
    tb = to_bytes(tp)
    art(tp, "변조본 (눈으로는 구별 불가)")
    a, b = sha(pb), sha(tb)
    diff = bin(int(a, 16) ^ int(b, 16)).count("1")
    kv("편집본 해시", short(a, 32))
    kv("변조본 해시", short(b, 32), color="red")
    kv("달라진 비트", f"{diff} / 256  (눈사태 효과)")
    res, vd = verify(tb, p1, trust, store)
    show(res, vd)
    say("서명이 깨진 게 아니다. 서명은 '해시'에 걸려 있고, 사진이 바뀌어 해시가 달라졌다.")

    # 5 ── 공격 B
    step("5) 공격 B — 딥페이크 이미지를 서명 없이 유포")
    fake = make_photo("fake")
    fb = to_bytes(fake)
    art(fake, "딥페이크 (서명 없음)")
    res, vd = verify(fb, None, trust, store)
    show(res, vd)
    say("'가짜다'가 아니라 '출처를 확인할 수 없다'. 서명된 진짜가 많아질수록 이 표시의 무게가 커진다.")

    # 6 ── 공격 C
    step("6) 공격 C — 공격자가 자기 키로 서명하되 작성자를 '로이터 통신'이라고 적는다")
    p_forge = make_manifest(evil, fb, "로이터 통신 · 현장 속보", "captured")
    store[mhash(p_forge["m"])] = p_forge
    res, vd = verify(fb, p_forge, trust, store)
    show(res, vd)
    say("서명 자체는 수학적으로 유효하다. 그러나 서명한 키가 신뢰 목록에 없다 → 신뢰는 키의 '등록'에서 나온다.")

    # 7 ── 정직한 AI
    step("7) 정직한 AI 생성 — 도구가 스스로 'AI 생성'이라고 서명해 남긴다")
    pg = make_manifest(gen, fb, "ImageGen 도구", "ai-generated:prompt-hash=" + sha(b"sunset")[:8])
    store[mhash(pg["m"])] = pg
    res, vd = verify(fb, pg, trust, store)
    show(res, vd)
    say("같은 이미지라도 출처가 선언되어 있으면 '속이는 가짜'가 아니라 '표시된 AI 콘텐츠'가 된다.")

    # 8 ── 앵커
    step("8) 블록체인 앵커링 — 촬영 매니페스트의 해시를 장부에 기록")
    ledger.add(["tx:other-1", "tx:other-2"])
    blk = ledger.add([h0, "tx:other-3"])
    ledger.add(["tx:other-4"])
    kv("앵커 기록", f"블록 #{blk['h']}  tx = {short(h0, 24)}")
    f = ledger.find(h0)
    good(f"누구나 조회: 이 매니페스트는 블록 #{f['h']} 시점에 이미 존재했다 (사후 조작·소급 불가)")
    ledger.blocks[1]["txs"][0] = "tx:rewritten"
    chain_ok = all(ledger.blocks[i]["prev"] == Ledger.bhash(ledger.blocks[i - 1]) for i in range(1, len(ledger.blocks)))
    if not chain_ok:
        good("장부를 고쳐 보면? → 뒤 블록의 prev 해시가 어긋나 즉시 드러남 (해시 체인)")
    say("블록체인은 사진을 저장하지 않는다. 해시 하나만 기록한다 — 시각 증명과 부인 방지 역할.")

    # 9 ── 한계
    step("9) 한계 — 무엇을 증명하고, 무엇을 증명하지 못하나")
    res, vd = verify(pb, None, trust, store)
    kv("메타데이터 제거", "스크린샷·재인코딩으로 서명 정보를 지우면")
    show(res, vd)
    bad("이 도구는 '내용이 진실인가'를 증명하지 않는다 — 출처와 편집 이력만 증명한다")
    bad("신뢰 목록과 기기 키 보관(탈취·유출)이 새로운 신뢰의 핵심 고리가 된다")
    bad("서명 없는 콘텐츠는 여전히 대다수 — 도입률이 효과를 좌우한다")

    done("정리: 해시(변조 탐지) + 서명(작성자 증명) + 해시 체인(편집 이력) + 블록체인(시각 증명) — 도구는 그대로, 대상만 AI 콘텐츠.")
    say("브라우저 시각화: 같은 명령에 --web")


if __name__ == "__main__":
    main()
