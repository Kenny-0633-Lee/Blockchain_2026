#!/usr/bin/env python3
"""
did_demo.py - 모바일 신분증(DID/VC) 구조 시뮬레이션 (교육용 개념 시연)

블록체인은 '코인'이 아니라 '위조할 수 없는 공개키 명부(Trust Anchor)'로 쓰인다.
  - 원장(허가형, 인가된 노드 4개 중 3개 이상 서명) : DID -> 공개키, 폐지 목록만 기록
  - 신분증 내용(VC)                                  : 휴대폰 지갑에만 저장 (체인에 없음)
  - 선택적 공개                                      : salt+해시 커밋먼트 (SD-JWT 유사 개념, ZK 아님)

주의: 실제 행안부/경찰청 모바일 신분증(OmniOne OpenDID)의 내부 구현과 동일하다고
      주장하지 않는 '개념 시뮬레이션'이다. DID 이름(did:kr:...)도 예시이다.

실행 (macOS 터미널 / Windows PowerShell 또는 Git Bash 공통):
    pip install cryptography          # Windows에서 python 이 안 되면 py 사용
    python did_demo.py                # Enter 로 단계 진행 (수업용)
    python did_demo.py --auto         # 멈춤 없이 한 번에
"""
import base64
import hashlib
import json
import os
import sys
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Windows 콘솔(cp949)에서도 한글/기호가 깨지지 않도록
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

AUTO = "--auto" in sys.argv or not sys.stdin.isatty()
OK, NO = "[ OK ]", "[FAIL]"


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


def step(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    if not AUTO:
        input("  (Enter) ")


def report(label: str, ok: bool, why: str = ""):
    print(f"  {OK if ok else NO} {label}" + (f"  <- {why}" if why else ""))


# ---------------------------------------------------------------- 허가형 원장
class PermissionedLedger:
    """인가된 노드 N개, 블록은 quorum(=2f+1) 이상 서명이 있어야 유효. (N=4, f=1 -> quorum 3)"""

    def __init__(self, n_nodes=4):
        self.nodes = {f"node{i+1}": new_key() for i in range(n_nodes)}
        self.node_pubs = {k: pub_b64(v) for k, v in self.nodes.items()}
        self.quorum = (2 * n_nodes) // 3 + 1  # 4 -> 3
        self.chain = []
        self._append([{"type": "GENESIS"}])

    def _append(self, txs):
        prev = self.chain[-1]["hash"] if self.chain else "0" * 64
        body = {"height": len(self.chain), "prev": prev, "txs": txs}
        h = sha256(canon(body))
        # 합의 단순화: 모든 정직한 노드가 같은 블록에 서명 (실제는 BFT 합의 프로토콜)
        sigs = {name: sign(k, h.encode()) for name, k in self.nodes.items()}
        self.chain.append({**body, "hash": h, "sigs": sigs})

    def submit(self, tx):
        self._append([tx])

    def validate(self, chain=None):
        """해시 연결 + 블록 해시 재계산 + 인가 노드 quorum 서명 확인"""
        chain = chain if chain is not None else self.chain
        prev = "0" * 64
        for blk in chain:
            body = {"height": blk["height"], "prev": blk["prev"], "txs": blk["txs"]}
            if blk["prev"] != prev:
                return False, f"블록 {blk['height']}: 이전 해시 연결이 끊김"
            if sha256(canon(body)) != blk["hash"]:
                return False, f"블록 {blk['height']}: 내용이 바뀜(해시 불일치)"
            good = sum(1 for n, s in blk["sigs"].items()
                       if n in self.node_pubs and verify(self.node_pubs[n], blk["hash"].encode(), s))
            if good < self.quorum:
                return False, f"블록 {blk['height']}: 유효 서명 {good} < quorum {self.quorum}"
            prev = blk["hash"]
        return True, "체인 전체 유효"

    # ----- 읽기 API (검증자가 사용) -----
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
    def __init__(self, did, ledger):
        self.did, self.key, self.ledger = did, new_key(), ledger
        ledger.submit({"type": "REGISTER_DID", "did": did, "pubkey": pub_b64(self.key)})

    def issue(self, holder_did, holder_pub, claims):
        """속성마다 (salt, 값) 을 해시 커밋 -> 해시 목록에 서명. 값 자체는 VC에 넣지 않는다."""
        salts = {k: base64.b64encode(os.urandom(16)).decode() for k in claims}
        digests = {k: sha256(canon([salts[k], k, v])) for k, v in claims.items()}
        status_id = sha256(os.urandom(16))[:16]
        vc = {"issuer": self.did, "holder": holder_did, "holder_pub": holder_pub,
              "digests": digests, "status_id": status_id}
        vc["sig"] = sign(self.key, canon(vc))
        return vc, salts  # salts 와 원본 claims 는 홀더(지갑)에게만 전달

    def revoke(self, vc):
        self.ledger.submit({"type": "REVOKE", "status_id": vc["status_id"]})


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

    def check(self, pres, ledger_view=None):
        """반환: (통과여부, [(항목, 결과, 사유)]) """
        res = []
        chain = ledger_view if ledger_view is not None else self.ledger.chain
        vc, proof = pres["vc"], pres["proof"]

        ok, why = self.ledger.validate(chain)
        res.append(("원장 무결성(해시 연결+quorum 서명)", ok, "" if ok else why))
        if not ok:
            return False, res

        issuer_pub = self.ledger.resolve(vc["issuer"], chain)
        res.append(("발급자 DID 가 원장에 등록됨", issuer_pub is not None,
                    "" if issuer_pub else f"{vc['issuer']} 미등록"))
        if not issuer_pub:
            return False, res

        body = {k: v for k, v in vc.items() if k != "sig"}
        ok = verify(issuer_pub, canon(body), vc["sig"])
        res.append(("발급자 서명(VC)", ok, "" if ok else "원장의 공개키로 검증 실패"))
        if not ok:
            return False, res

        bad = [k for k, (salt, val) in pres["reveal"].items()
               if sha256(canon([salt, k, val])) != vc["digests"].get(k)]
        res.append(("공개한 속성이 서명된 해시와 일치", not bad,
                    "" if not bad else f"불일치: {bad}"))
        if bad:
            return False, res

        ok = (proof["nonce"] in self.pending and proof["domain"] == self.domain
              and proof["vc_hash"] == sha256(canon(vc)))
        res.append(("nonce/도메인 일치(재사용 방지)", ok,
                    "" if ok else "내가 낸 nonce 가 아니거나 다른 도메인용"))
        if not ok:
            return False, res

        ok = verify(vc["holder_pub"], canon(proof), pres["holder_sig"])
        res.append(("홀더 서명(이 폰의 키 소유 증명)", ok, "" if ok else "서명 불일치"))
        if not ok:
            return False, res

        revoked = self.ledger.is_revoked(vc["status_id"], chain)
        res.append(("폐지(정지) 여부", not revoked, "원장에 폐지 기록 있음" if revoked else ""))
        if revoked:
            return False, res

        self.pending.discard(proof["nonce"])  # 한 번 쓴 nonce 는 폐기
        return True, res


def show(ok, res):
    for label, passed, why in res:
        report(label, passed, why)
    print(f"  => 검증 결과: {'수락' if ok else '거부'}")


# ---------------------------------------------------------------- 시연
def main():
    t0 = time.time()
    step("0. 허가형 원장 생성 — 인가된 노드 4개, 블록은 3개 이상 서명해야 유효")
    ledger = PermissionedLedger(4)
    print(f"  노드: {list(ledger.nodes)} / quorum = {ledger.quorum} (n=4, f=1 -> 3f+1 모델)")

    step("1. 발급기관 DID 등록 — 원장에는 'DID -> 공개키'만 올라간다")
    police = Issuer("did:kr:police-demo", ledger)
    blk = ledger.chain[-1]
    print(f"  블록 {blk['height']} hash={short(blk['hash'])} 서명 {len(blk['sigs'])}개")
    print(f"  기록된 내용: {json.dumps(blk['txs'][0], ensure_ascii=False)[:110]}…")
    print("  ※ 이름/생년월일 같은 개인정보는 원장에 없다.")

    step("2. 발급 — 속성별 salt+해시에 발급기관이 서명, 값은 폰(지갑)에만 저장")
    alice = Wallet("did:kr:holder-alice")
    claims = {"name": "홍길동", "birth": "2003-05-17", "address": "대구 북구 대학로 80",
              "license_class": "1종 보통", "adult_19": True}
    vc, salts = police.issue(alice.did, pub_b64(alice.key), claims)
    alice.store(vc, salts, claims)
    print("  VC 에 들어간 것(해시만):")
    for k, d in vc["digests"].items():
        print(f"    {k:<14} {short(d, 20)}")
    print(f"  발급기관 서명: {short(vc['sig'], 24)}")

    step("3. 정상 검증 — 편의점(검증자)이 '성인 여부'만 요구")
    cvs = Verifier("convenience-store.example", ledger)
    nonce = cvs.challenge()
    pres = alice.present(nonce, cvs.domain, disclose=["adult_19"])
    print(f"  검증자가 받은 속성: {pres['reveal']}")
    print(f"  이름/생년월일/주소를 검증자가 알 수 있는가? -> {'name' in pres['reveal']}")
    ok, res = cvs.check(pres)
    show(ok, res)

    step("4-A. 공격: 가짜 발급기관 — 공격자가 자기 키로 만든 VC")
    mallory_key = new_key()
    fake_vc = {"issuer": "did:kr:police-demo", "holder": alice.did, "holder_pub": pub_b64(alice.key),
               "digests": vc["digests"], "status_id": "deadbeef"}
    fake_vc["sig"] = sign(mallory_key, canon(fake_vc))  # 개인키가 다르다
    fake = Wallet("did:kr:holder-alice"); fake.key = alice.key
    fake.store(fake_vc, salts, claims)
    n = cvs.challenge()
    ok, res = cvs.check(fake.present(n, cvs.domain, ["adult_19"]))
    show(ok, res)
    print("  -> 이름만 'did:kr:police-demo' 라고 써도, 원장에 등록된 공개키로 검증하므로 통과 못 한다.")

    step("4-B. 공격: 공개 값 변조 — 미성년자가 adult_19 를 False -> True 로 조작")
    young = Wallet("did:kr:holder-bob")
    yclaims = dict(claims, birth="2010-01-01", adult_19=False)
    yvc, ysalts = police.issue(young.did, pub_b64(young.key), yclaims)
    young.store(yvc, ysalts, yclaims)
    n = cvs.challenge()
    p = young.present(n, cvs.domain, ["adult_19"])
    p["reveal"]["adult_19"][1] = True  # 미성년자가 값을 True 로 조작
    ok, res = cvs.check(p)
    show(ok, res)

    step("4-C. 공격: 재사용(replay) — 편의점에서 가로챈 응답을 술집에 그대로 제출")
    n = cvs.challenge()
    captured = alice.present(n, cvs.domain, ["adult_19"])
    pub_bar = Verifier("bar.example", ledger)
    pub_bar.pending.add(n)  # 최악의 가정: 술집이 같은 nonce 를 쓴다고 해도
    ok, res = pub_bar.check(captured)
    show(ok, res)
    print("  -> 응답이 '도메인+nonce'에 묶여 있어 다른 곳에서는 쓸 수 없다.")

    step("4-D. 원장 위·변조 — 공격자가 발급기관 공개키를 자기 키로 바꾸려는 시도")
    forged_chain = json.loads(json.dumps(ledger.chain))
    forged_chain[1]["txs"][0]["pubkey"] = pub_b64(mallory_key)
    n = cvs.challenge()
    ok, res = cvs.check(alice.present(n, cvs.domain, ["adult_19"]), ledger_view=forged_chain)
    show(ok, res)
    print("  -> 한 블록을 바꾸면 해시가 달라지고, 정직한 노드 서명을 위조할 수 없다.")

    step("4-E. 폐지 — 면허 정지/분실 신고 후 같은 신분증으로 제출")
    police.revoke(alice.vc)
    print(f"  원장에 REVOKE 기록(블록 {len(ledger.chain)-1}): status_id={alice.vc['status_id']}")
    n = cvs.challenge()
    ok, res = cvs.check(alice.present(n, cvs.domain, ["adult_19"]))
    show(ok, res)
    print("  -> 검증자는 발급기관에 전화하지 않고 원장만 보고 폐지 여부를 안다.")

    step("5. 선택적 공개 — 같은 VC 로 서로 다른 검증자에게 다른 속성만 공개")
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
        ok, _ = vf.check(p)
        print(f"  {who:<4} 에게 공개: {attrs}  -> {'수락' if ok else '거부'}  (숨겨진 속성 {len(c2)-len(attrs)}개)")
    print("  숨긴 속성의 해시는 salt 가 있어 값을 추측(사전 대입)할 수 없다.")
    print("  예) birth 해시는 2003-05-17 같은 날짜를 전부 대입해 봐도 salt 를 모르면 맞출 수 없음.")

    print("\n" + "-" * 70)
    print("정리")
    print("  - 체인에 있는 것: DID -> 공개키, 폐지 기록 (개인정보 없음)")
    print("  - 폰에 있는 것 : 신분증 내용 + 개인키 (밖으로 나가지 않음)")
    print("  - 검증자가 하는 일: 원장 조회 + 서명/해시 검증 (발급기관 서버 호출 없이)")
    print(f"  (실행 시간 {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
