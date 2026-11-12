#!/usr/bin/env python3
"""
did_demo.py - 모바일 신분증(DID/VC) 구조 시뮬레이션 (교육용 개념 시연)

블록체인은 '코인'이 아니라 '위조할 수 없는 공개키 명부(Trust Anchor)'로 쓰인다.
  - 원장(허가형, 인가된 노드 4개 중 3개 이상 서명) : DID -> 공개키, 폐지 목록만 기록
  - 신분증 내용(VC)                                  : 휴대폰 지갑에만 저장 (체인에 없음)
  - 선택적 공개                                      : salt+해시 커밋먼트 (SD-JWT 유사 개념, ZK 아님)

주의: 실제 행안부/경찰청 모바일 신분증(OmniOne OpenDID)의 내부 구현과 동일하다고
      주장하지 않는 '개념 시뮬레이션'이다. DID 이름(did:kr:...)도 예시이다.

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
  0 원장 생성 / 1 발급기관 DID 등록 / 2 신분증 발급 / 3 정상 검증
  4-A 가짜 발급기관 / 4-B 값 변조 / 4-C 재사용(replay) / 4-D 원장 위·변조 / 4-E 폐지
  5 선택적 공개

실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
    uv run python special_topic_2026/05_did_mobile_id/did_demo.py
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)
"""
import base64
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (bad, c, done, good, kv, line, pause, say, sleep, step, title)


# ---------------------------------------------------------------- 유틸
def canon(obj) -> bytes:
    """서명 대상 직렬화: 키 정렬 + 공백 제거 (같은 데이터 = 같은 바이트)"""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def new_key():
    return ec.generate_private_key(ec.SECP256R1())  # 모바일 보안영역에서 흔한 P-256


def pub_b64(priv) -> str:
    raw = priv.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return base64.b64encode(raw).decode()


def load_pub(b64: str):
    return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), base64.b64decode(b64))


def sign(priv, data: bytes) -> str:
    return base64.b64encode(priv.sign(data, ec.ECDSA(hashes.SHA256()))).decode()


def verify(pub_b64_str: str, data: bytes, sig_b64: str) -> bool:
    try:
        load_pub(pub_b64_str).verify(base64.b64decode(sig_b64), data, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError):
        return False


def short(s: str, n=12) -> str:
    return s[:n] + "…"


def fp(pub: str) -> str:
    """공개키 지문(앞 10자리)"""
    return sha256(base64.b64decode(pub))[:10]


# ---------------------------------------------------------------- 허가형 원장
class PermissionedLedger:
    """인가된 노드 N개, 블록은 quorum(=2f+1) 이상 서명이 있어야 유효. (N=4, f=1 -> quorum 3)"""

    def __init__(self, n_nodes=4, verbose=False):
        self.nodes = {}
        for i in range(n_nodes):
            k = new_key()
            self.nodes[f"node{i + 1}"] = k
            if verbose:
                line(f"  node{i + 1} 키 생성   공개키 지문 {c(fp(pub_b64(k)), 'cyan')}", 0.35)
        self.node_pubs = {k: pub_b64(v) for k, v in self.nodes.items()}
        self.quorum = (2 * n_nodes) // 3 + 1  # 4 -> 3
        self.chain = []
        self._append([{"type": "GENESIS"}])

    def _append(self, txs, verbose=False):
        prev = self.chain[-1]["hash"] if self.chain else "0" * 64
        body = {"height": len(self.chain), "prev": prev, "txs": txs}
        h = sha256(canon(body))
        if verbose:
            kv("블록 번호", str(body["height"]), width=12)
            kv("이전 해시", short(prev, 16), width=12)
            kv("거래", json.dumps(txs[0], ensure_ascii=False)[:78] + ("…" if len(json.dumps(txs[0])) > 78 else ""), width=12)
            kv("블록 해시", c(short(h, 16), "cyan"), width=12)
        # 합의 단순화: 모든 정직한 노드가 같은 블록에 서명 (실제는 BFT 합의 프로토콜)
        sigs = {}
        for name, k in self.nodes.items():
            sigs[name] = sign(k, h.encode())
            if verbose:
                line(f"    {name} 서명 {c('✔', 'green')}  {short(sigs[name], 14)}   "
                     f"({len(sigs)}/{len(self.nodes)}, quorum {self.quorum})", 0.3)
        self.chain.append({**body, "hash": h, "sigs": sigs})

    def submit(self, tx, verbose=False):
        self._append([tx], verbose)

    def validate(self, chain=None):
        """해시 연결 + 블록 해시 재계산 + 인가 노드 quorum 서명 확인"""
        chain = chain if chain is not None else self.chain
        prev = "0" * 64
        for blk in chain:
            body = {"height": blk["height"], "prev": blk["prev"], "txs": blk["txs"]}
            if blk["prev"] != prev:
                return False, f"블록 {blk['height']}: 이전 해시 연결이 끊김"
            recomputed = sha256(canon(body))
            if recomputed != blk["hash"]:
                return False, (f"블록 {blk['height']}: 내용이 바뀜 (기록된 해시 {short(blk['hash'], 8)} ≠ "
                               f"다시 계산한 해시 {short(recomputed, 8)})")
            good_n = sum(1 for n, s in blk["sigs"].items()
                         if n in self.node_pubs and verify(self.node_pubs[n], blk["hash"].encode(), s))
            if good_n < self.quorum:
                return False, f"블록 {blk['height']}: 유효 서명 {good_n} < quorum {self.quorum}"
            prev = blk["hash"]
        return True, f"체인 {len(chain)}개 블록 전체 유효 (해시 연결 + 노드 서명)"

    def resolve(self, did, chain=None):
        key = None
        for blk in (chain if chain is not None else self.chain):
            for tx in blk["txs"]:
                if tx.get("type") == "REGISTER_DID" and tx["did"] == did:
                    key = tx["pubkey"]
        return key

    def is_revoked(self, status_id, chain=None):
        for blk in (chain if chain is not None else self.chain):
            for tx in blk["txs"]:
                if tx.get("type") == "REVOKE" and tx["status_id"] == status_id:
                    return True
        return False


# ---------------------------------------------------------------- 발급자
class Issuer:
    def __init__(self, did, ledger, verbose=False):
        self.did, self.key, self.ledger = did, new_key(), ledger
        if verbose:
            kv("발급기관 DID", did, width=12)
            kv("개인키", "발급기관 서버에만 보관 (밖으로 나가지 않음)", width=12)
            kv("공개키 지문", c(fp(pub_b64(self.key)), "cyan"), width=12)
            sleep(0.4)
        ledger.submit({"type": "REGISTER_DID", "did": did, "pubkey": pub_b64(self.key)}, verbose)

    def issue(self, holder_did, holder_pub, claims, verbose=False):
        """속성마다 (salt, 값) 을 해시 커밋 -> 해시 목록에 서명. 값 자체는 VC에 넣지 않는다."""
        salts = {k: base64.b64encode(os.urandom(16)).decode() for k in claims}
        digests = {}
        for k, v in claims.items():
            digests[k] = sha256(canon([salts[k], k, v]))
            if verbose:
                line(f"  {k:<14} 값={c(str(v), 'bold'):<24} salt={short(salts[k], 8)}  "
                     f"→ SHA256 = {c(short(digests[k], 16), 'cyan')}", 0.45)
        status_id = sha256(os.urandom(16))[:16]
        vc = {"issuer": self.did, "holder": holder_did, "holder_pub": holder_pub,
              "digests": digests, "status_id": status_id}
        vc["sig"] = sign(self.key, canon(vc))
        if verbose:
            sleep(0.3)
            kv("VC 본문 해시", short(sha256(canon({k: v for k, v in vc.items() if k != 'sig'})), 16), width=14)
            kv("발급기관 서명", c(short(vc["sig"], 24), "cyan"), width=14)
        return vc, salts

    def revoke(self, vc, verbose=False):
        self.ledger.submit({"type": "REVOKE", "status_id": vc["status_id"]}, verbose)


# ---------------------------------------------------------------- 홀더(지갑)
class Wallet:
    def __init__(self, did):
        self.did, self.key = did, new_key()
        self.vc = self.salts = self.claims = None

    def store(self, vc, salts, claims):
        self.vc, self.salts, self.claims = vc, salts, claims

    def present(self, nonce, domain, disclose):
        """필요한 속성만 (salt, 값) 공개 + (nonce, 도메인, VC 해시)에 홀더 서명"""
        reveal = {k: [self.salts[k], self.claims[k]] for k in disclose}
        proof = {"nonce": nonce, "domain": domain, "vc_hash": sha256(canon(self.vc))}
        return {"vc": self.vc, "reveal": reveal, "proof": proof,
                "holder_sig": sign(self.key, canon(proof))}


# ---------------------------------------------------------------- 검증자
class Verifier:
    def __init__(self, domain, ledger):
        self.domain, self.ledger = domain, ledger
        self.pending = set()

    def challenge(self):
        n = base64.b64encode(os.urandom(12)).decode()
        self.pending.add(n)
        return n

    def check(self, pres, ledger_view=None, live=True):
        """검증 항목을 하나씩 수행하며 결과를 즉시 출력. 반환: (통과여부, 실패항목)"""
        chain = ledger_view if ledger_view is not None else self.ledger.chain
        vc, proof = pres["vc"], pres["proof"]
        state = {"ok": True, "failed": None}

        def r(label, passed, detail="", why="", keep_detail=False):
            """실패 줄에는 '통과' 같은 성공 설명을 붙이지 않는다 (keep_detail=True 인 항목만 예외)"""
            if live:
                sleep(0.45)
                mark = c("[ OK ]", "green") if passed else c("[FAIL]", "red", "bold")
                show_detail = detail if (passed or keep_detail) else ""
                print(f"  {mark} {label}" + (c(f"   {show_detail}", "dim") if show_detail else "")
                      + (c(f"  ← {why}", "red") if (not passed and why) else ""))
            if not passed:
                state["ok"], state["failed"] = False, label
            return passed

        ok, why = self.ledger.validate(chain)
        if not r("① 원장 무결성 (해시 연결 + 노드 서명 quorum)", ok, "" if not ok else why, why if not ok else ""):
            return False, state["failed"]

        issuer_pub = self.ledger.resolve(vc["issuer"], chain)
        if not r("② 발급자 DID 가 원장에 등록됨", issuer_pub is not None,
                 f"{vc['issuer']} → 공개키 지문 {fp(issuer_pub)}" if issuer_pub else "",
                 f"{vc['issuer']} 미등록"):
            return False, state["failed"]

        body = {k: v for k, v in vc.items() if k != "sig"}
        ok = verify(issuer_pub, canon(body), vc["sig"])
        if not r("③ 발급자 서명 (VC 전체)", ok, "원장의 공개키로 서명 검증 통과", "원장의 공개키로 검증 실패 (다른 키로 서명됨)"):
            return False, state["failed"]

        bad_keys = [k for k, (salt, val) in pres["reveal"].items()
                    if sha256(canon([salt, k, val])) != vc["digests"].get(k)]
        shown = ", ".join(f"{k}={v[1]}" for k, v in pres["reveal"].items())
        if not r("④ 공개한 속성이 서명된 해시와 일치", not bad_keys, f"공개: {shown}",
                 f"불일치 속성 {bad_keys}: 다시 계산한 해시 ≠ 서명된 해시", keep_detail=True):
            return False, state["failed"]

        ok = (proof["nonce"] in self.pending and proof["domain"] == self.domain
              and proof["vc_hash"] == sha256(canon(vc)))
        if not r("⑤ nonce·도메인 일치 (재사용 방지)", ok,
                 f"nonce {short(proof['nonce'], 8)} / 도메인 {proof['domain']}",
                 f"내가({self.domain}) 낸 nonce 가 아니거나 다른 도메인({proof['domain']})용 응답", keep_detail=False):
            return False, state["failed"]

        ok = verify(vc["holder_pub"], canon(proof), pres["holder_sig"])
        if not r("⑥ 홀더 서명 (이 폰의 개인키 소유 증명)", ok, "VC 에 적힌 홀더 공개키로 검증 통과", "서명 불일치"):
            return False, state["failed"]

        revoked = self.ledger.is_revoked(vc["status_id"], chain)
        if not r("⑦ 폐지(정지) 여부", not revoked, f"status_id {vc['status_id'][:8]}… 폐지 기록 없음",
                 "원장에 폐지 기록 있음"):
            return False, state["failed"]

        self.pending.discard(proof["nonce"])  # 한 번 쓴 nonce 는 폐기
        return True, None


def verdict(ok, failed=None):
    if ok:
        print("  " + c("⇒ 검증 결과: 수락 ✔", "green", "bold"))
    else:
        print("  " + c(f"⇒ 검증 결과: 거부 ✘  (실패 지점: {failed})", "red", "bold"))


# ---------------------------------------------------------------- 시연
def main():
    t0 = time.time()
    title("모바일 신분증(DID/VC) — 코인이 아닌 블록체인")
    say("체인에 있는 것: DID → 공개키, 폐지 기록 / 폰에 있는 것: 신분증 내용 + 개인키")

    step("0. 허가형 원장을 만든다 — 인가된 노드 4개, 블록은 3개 이상 서명해야 유효")
    say("누구나 참여하는 비트코인과 달리, 참여 기관이 정해져 있다 (허가형, permissioned).")
    ledger = PermissionedLedger(4, verbose=True)
    kv("quorum", f"{ledger.quorum} / 4   (n = 3f + 1 = 4, f = 1 : 노드 1개가 틀려도 안전)", width=8)

    step("1. 발급기관(경찰청 역할)이 자기 DID 와 공개키를 원장에 등록한다")
    police = Issuer("did:kr:police-demo", ledger, verbose=True)
    say("원장에는 개인정보가 없다. 'did:kr:police-demo 의 공개키는 이것'이라는 사실만 기록된다.")

    step("2. 발급 — 속성마다 (salt + 값)을 해시로 묶고, 발급기관이 서명한다")
    say("값 자체는 VC 에 넣지 않는다. 값은 지갑(폰)에만 있고, VC 에는 해시만 있다.")
    alice = Wallet("did:kr:holder-alice")
    claims = {"name": "홍길동", "birth": "2003-05-17", "address": "대구 북구 대학로 80",
              "license_class": "1종 보통", "adult_19": True}
    kv("홀더", f"{alice.did}  (키쌍은 폰 보안영역에서 생성, 공개키 지문 {fp(pub_b64(alice.key))})", width=6)
    vc, salts = police.issue(alice.did, pub_b64(alice.key), claims, verbose=True)
    alice.store(vc, salts, claims)
    say("이 VC(해시 목록 + 서명)와 원본 값·salt 가 홀더 폰에 저장된다.")

    step("3. 정상 검증 — 편의점(검증자)이 '성인 여부'만 요구한다")
    cvs = Verifier("convenience-store.example", ledger)
    nonce = cvs.challenge()
    kv("검증자 → 폰", f"챌린지 nonce {short(nonce, 12)}, 요청 속성 = adult_19", width=12)
    pres = alice.present(nonce, cvs.domain, disclose=["adult_19"])
    kv("폰 → 검증자", f"공개 속성 {pres['reveal']['adult_19'][1]!r} + salt, VC, 홀더 서명", width=12)
    print(f"  이름·생년월일·주소가 검증자에게 전달되었는가? → {c(str('name' in pres['reveal']), 'bold')}")
    pause("Enter ▶ 검증 7항목 실행")
    ok, failed = cvs.check(pres)
    verdict(ok, failed)

    step("4-A. 공격: 가짜 발급기관 — 공격자가 자기 키로 'did:kr:police-demo' 라고 적어 서명")
    mallory_key = new_key()
    fake_vc = {"issuer": "did:kr:police-demo", "holder": alice.did, "holder_pub": pub_b64(alice.key),
               "digests": vc["digests"], "status_id": "deadbeef"}
    fake_vc["sig"] = sign(mallory_key, canon(fake_vc))
    kv("공격자 공개키 지문", c(fp(pub_b64(mallory_key)), "red"), width=18)
    kv("원장의 경찰 공개키", c(fp(pub_b64(police.key)), "green"), width=18)
    fake = Wallet(alice.did)
    fake.key = alice.key
    fake.store(fake_vc, salts, claims)
    n = cvs.challenge()
    pause("Enter ▶ 검증")
    ok, failed = cvs.check(fake.present(n, cvs.domain, ["adult_19"]))
    verdict(ok, failed)
    say("이름만 'did:kr:police-demo' 라고 써도, 검증자는 '원장에 등록된 공개키'로 확인하므로 통과할 수 없다.")

    step("4-B. 공격: 값 변조 — 미성년자가 adult_19 를 False → True 로 바꿔서 제출")
    young = Wallet("did:kr:holder-bob")
    yclaims = dict(claims, birth="2010-01-01", adult_19=False)
    yvc, ysalts = police.issue(young.did, pub_b64(young.key), yclaims)
    young.store(yvc, ysalts, yclaims)
    n = cvs.challenge()
    p = young.present(n, cvs.domain, ["adult_19"])
    print(f"  원래 값: adult_19 = {c('False', 'green')}  (발급기관이 서명한 해시는 이 값 기준)")
    p["reveal"]["adult_19"][1] = True
    print(f"  제출 값: adult_19 = {c('True', 'red', 'bold')}  (공격자가 조작)")
    pause("Enter ▶ 검증")
    ok, failed = cvs.check(p)
    verdict(ok, failed)
    say("값을 바꾸면 SHA256(salt‖속성‖값)이 달라져, 발급기관이 서명한 해시와 맞지 않는다.")

    step("4-C. 공격: 재사용(replay) — 편의점에서 가로챈 응답을 술집에 그대로 제출")
    n = cvs.challenge()
    captured = alice.present(n, cvs.domain, ["adult_19"])
    print(f"  가로챈 응답은 도메인 '{cvs.domain}' 의 nonce {short(n, 8)} 에 묶여 서명되어 있다.")
    bar_v = Verifier("bar.example", ledger)
    bar_v.pending.add(n)   # 최악의 가정: 술집이 같은 nonce 를 쓴다고 해도
    pause("Enter ▶ 술집(bar.example)이 검증")
    ok, failed = bar_v.check(captured)
    verdict(ok, failed)
    say("응답이 '도메인 + 일회용 nonce'에 묶여 있어 다른 곳·다른 시간에는 쓸 수 없다.")

    step("4-D. 공격: 원장 위·변조 — 공격자가 발급기관 공개키를 자기 키로 바꾼 복사본 원장")
    forged_chain = json.loads(json.dumps(ledger.chain))
    orig = forged_chain[1]["txs"][0]["pubkey"]
    forged_chain[1]["txs"][0]["pubkey"] = pub_b64(mallory_key)
    kv("블록 1 공개키", f"{fp(orig)} → {c(fp(pub_b64(mallory_key)), 'red')}  (공격자 키로 교체)", width=14)
    n = cvs.challenge()
    pause("Enter ▶ 검증")
    ok, failed = cvs.check(alice.present(n, cvs.domain, ["adult_19"]), ledger_view=forged_chain)
    verdict(ok, failed)
    say("블록 내용이 바뀌면 해시가 달라지고, 정직한 노드 4개의 서명을 위조할 수도 없다.")

    step("4-E. 폐지 — 면허 정지/분실 신고 후 같은 신분증으로 제출")
    say("발급기관이 원장에 폐지 기록(REVOKE)을 올린다.")
    police.revoke(alice.vc, verbose=True)
    n = cvs.challenge()
    pause("Enter ▶ 같은 신분증으로 다시 제출")
    ok, failed = cvs.check(alice.present(n, cvs.domain, ["adult_19"]))
    verdict(ok, failed)
    say("검증자는 발급기관에 전화하지 않고, 원장만 보고 폐지 여부를 안다.")

    step("5. 선택적 공개 — 같은 신분증으로 가게마다 필요한 속성만 보여 준다")
    ledger2 = PermissionedLedger(4)
    police2 = Issuer("did:kr:police-demo", ledger2)
    w = Wallet("did:kr:holder-carol")
    c2 = {"name": "이영희", "birth": "1999-11-02", "address": "서울 강남구",
          "license_class": "2종 보통", "adult_19": True}
    v2, s2 = police2.issue(w.did, pub_b64(w.key), c2)
    w.store(v2, s2, c2)
    for who, attrs in [("편의점", ["adult_19"]), ("렌터카", ["name", "license_class"]),
                       ("은행", ["name", "birth", "address"])]:
        vf = Verifier(f"{who}.example", ledger2)
        p = w.present(vf.challenge(), vf.domain, attrs)
        okk, _ = vf.check(p, live=False)
        hidden = [k for k in c2 if k not in attrs]
        print(f"\n  {c(who, 'bold')} 에게 공개: {', '.join(f'{k}={c2[k]}' for k in attrs)}")
        print(f"        숨김  : {', '.join(hidden)}   → 검증 {'수락 ✔' if okk else '거부 ✘'}")
        sleep(0.8)
        pause("Enter ▶ 다음 가게")
    say("숨긴 속성의 해시는 salt(무작위 16바이트)가 있어, 날짜를 전부 대입해 봐도 값을 추측할 수 없다.")

    done("정리: 체인 = 위조 불가능한 공개키 명부 + 폐지 목록 / 개인정보 = 폰 / 검증 = 원장 조회 + 서명·해시 확인")
    say(f"(총 실행 시간 {time.time() - t0:.1f}s, 대부분은 Enter 대기)")


if __name__ == "__main__":
    main()
