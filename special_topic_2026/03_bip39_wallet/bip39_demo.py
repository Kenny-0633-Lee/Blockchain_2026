"""
03_bip39_wallet/bip39_demo.py  (특강 2026-11-25)
================================================
BIP-39 니모닉 -> 시드 -> 개인키 -> 공개키 -> 주소 (Bitcoin / Ethereum)

진행 (Enter 로 한 단계씩, a = 끝까지, q = 종료)
  1) 난수 128비트(엔트로피) 만들기
  2) 체크섬 4비트 붙이고 11비트씩 12조각 -> 단어장 번호 -> 단어
  3) 니모닉 -> 시드: PBKDF2 2048회 (진행률이 보인다)
  4) 시드 -> BIP-44 경로(m/44'/coin'/0'/0/0)를 한 단계씩 내려가며 키 도출
  5) 공개키 -> Bitcoin 주소 (SHA256 -> RIPEMD160 -> 체크섬 -> Base58)
  6) 공개키 -> Ethereum 주소 (Keccak256 -> 뒤 20바이트)
  7) 복구 / 오타 / 25번째 단어

실행 (저장소 루트에서, macOS 터미널 / Windows PowerShell·Git Bash 공통)
  uv run python special_topic_2026/03_bip39_wallet/bip39_demo.py
옵션: --auto(멈춤 없이) --fast(애니메이션 없이)

교육용입니다. 여기서 만든 니모닉에 실제 자산을 넣지 마세요.
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common.demo_kit import (bad, bar, c, done, good, kv, line, live, live_end, pause, say, sleep,
                              step, title)

try:
    from bip_utils import (Base58Encoder, Bip39Languages, Bip39MnemonicGenerator,
                           Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Changes,
                           Bip44Coins)
    from bip_utils.utils.crypto import Hash160
    try:
        from bip_utils import Keccak256
    except ImportError:            # 일부 버전은 철자가 Kekkak256
        from bip_utils import Kekkak256 as Keccak256
except ImportError:
    print("패키지 필요: uv sync  (또는 pip install bip-utils)")
    sys.exit(1)

try:
    from bip_utils.bip.bip39.bip39_mnemonic_utils import Bip39WordsListGetter
    WORDS = Bip39WordsListGetter().GetByLanguage(Bip39Languages.ENGLISH)
except Exception:
    WORDS = None


def pbkdf2_with_progress(password: bytes, salt: bytes, rounds=2048):
    """PBKDF2-HMAC-SHA512 를 직접 구현해 진행률을 보인다 (결과는 hashlib 과 대조)"""
    u = hmac.new(password, salt + (1).to_bytes(4, "big"), hashlib.sha512).digest()
    t = int.from_bytes(u, "big")
    for i in range(2, rounds + 1):
        u = hmac.new(password, u, hashlib.sha512).digest()
        t ^= int.from_bytes(u, "big")
        if i % 64 == 0 or i == rounds:
            live(f"  PBKDF2 {i:>4}/{rounds}  {bar(i / rounds, 30)}  중간값 {u.hex()[:12]}…")
            sleep(0.03)
    live_end(f"  PBKDF2 {rounds}/{rounds}  {bar(1, 30)}  완료")
    return t.to_bytes(64, "big")


def wallet(mnemonic, passphrase=""):
    seed = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    out = {}
    for name, coin in (("Bitcoin", Bip44Coins.BITCOIN), ("Ethereum", Bip44Coins.ETHEREUM)):
        a = (Bip44.FromSeed(seed, coin).Purpose().Coin().Account(0)
             .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0))
        out[name] = a.PublicKey().ToAddress()
    return out


def main():
    title("BIP-39 — 12단어가 어떻게 지갑이 되는가")

    step("1. 난수 128비트 (엔트로피) 를 만든다")
    ent = os.urandom(16)
    bits = "".join(f"{b:08b}" for b in ent)
    for i in range(0, 128, 32):
        line(f"  {bits[i:i + 32]}", 0.25)
    kv("16진수", ent.hex())
    say("이 128비트가 지갑의 전부다. 추측할 수 없을 만큼 무작위여야 한다 (2^128 가지).")

    step("2. 체크섬 4비트를 붙이고 11비트씩 잘라 단어로 바꾼다")
    chk = bin(hashlib.sha256(ent).digest()[0])[2:].zfill(8)[:4]
    allbits = bits + chk
    kv("체크섬", f"SHA256(엔트로피)의 첫 4비트 = {c(chk, 'yellow')}")
    kv("합계", f"128 + 4 = {len(allbits)} 비트 = 11비트 × 12")
    words = []
    for k in range(12):
        chunk = allbits[k * 11:(k + 1) * 11]
        idx = int(chunk, 2)
        word = WORDS.GetWordAtIdx(idx) if WORDS else "?"
        words.append(word)
        line(f"  {k + 1:>2}) {c(chunk, 'cyan')}  →  번호 {idx:>4}  →  {c(word, 'green', 'bold')}", 0.3)
    mnemonic = " ".join(words)
    lib = str(Bip39MnemonicGenerator(Bip39Languages.ENGLISH).FromEntropy(ent))
    if WORDS:
        (good if lib == mnemonic else bad)(f"라이브러리 결과와 일치: {lib == mnemonic}")
    else:
        mnemonic = lib
        say("(단어장 조회를 못 해 라이브러리 결과를 사용)")
    print("\n  " + c(mnemonic, "bold", "green"))
    say("단어장 2048개 = 2^11.  단어 12개를 적어 두면 128비트가 복원된다 (사람이 옮겨 적기 쉬움).")

    step("3. 니모닉 → 시드: PBKDF2-HMAC-SHA512, 2048회 반복 (무차별 대입을 느리게 만든다)")
    kv("password", "니모닉 문장 전체", width=10)
    kv("salt", '"mnemonic" + passphrase(지금은 빈 문자열)', width=10)
    seed = pbkdf2_with_progress(mnemonic.encode(), b"mnemonic")
    lib_seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode(), b"mnemonic", 2048)
    print(f"  시드(64바이트): {seed.hex()[:48]}…")
    (good if seed == lib_seed == Bip39SeedGenerator(mnemonic).Generate() else bad)(
        "직접 계산한 시드 = hashlib = bip_utils 결과 일치")

    step("4. 시드 → BIP-44 경로 m / 44' / coin' / 0' / 0 / 0 를 한 단계씩 내려간다")
    say("각 단계마다 부모 키에서 자식 키가 결정적으로 나온다 (같은 시드 = 같은 키 트리).")
    for name, coin, cn in (("Bitcoin", Bip44Coins.BITCOIN, "0'"), ("Ethereum", Bip44Coins.ETHEREUM, "60'")):
        print(c(f"\n  [{name}]", "yellow", "bold"))
        node = Bip44.FromSeed(seed, coin)
        pk = lambda n: n.PublicKey().RawCompressed().ToHex()[:16]
        steps_ = [("m (마스터)", node)]
        node = node.Purpose()
        steps_.append(("m/44'", node))
        node = node.Coin()
        steps_.append((f"m/44'/{cn}", node))
        node = node.Account(0)
        steps_.append((f"m/44'/{cn}/0'", node))
        node = node.Change(Bip44Changes.CHAIN_EXT)
        steps_.append((f"m/44'/{cn}/0'/0", node))
        node = node.AddressIndex(0)
        steps_.append((f"m/44'/{cn}/0'/0/0", node))
        for label, n in steps_:
            line(f"    {label:<22} 공개키 {pk(n)}…", 0.3)
        kv("  최종 개인키", node.PrivateKey().Raw().ToHex()[:16] + "… (절대 공개 금지)", width=14, color="red")
        if name == "Bitcoin":
            btc_node = node
        else:
            eth_node = node
        pause("Enter ▶ 다음")

    step("5. 공개키 → Bitcoin 주소")
    comp = btc_node.PublicKey().RawCompressed().ToBytes()
    sha = hashlib.sha256(comp).digest()
    h160 = Hash160.QuickDigest(comp)   # = RIPEMD160(SHA256(공개키)), OpenSSL 설정과 무관하게 동작
    payload = b"\x00" + h160
    chksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    addr = Base58Encoder.CheckEncode(payload)
    kv("압축 공개키", comp.hex()[:30] + "…", width=16)
    kv("SHA-256", sha.hex()[:30] + "…", width=16)
    kv("RIPEMD-160", h160.hex() + " (= HASH160, 20바이트)", width=16)
    kv("버전 바이트", "00 (메인넷 P2PKH)", width=16)
    kv("체크섬", f"더블 SHA-256 의 앞 4바이트 = {chksum.hex()}", width=16)
    kv("Base58", addr, width=16, color="green")
    (good if addr == btc_node.PublicKey().ToAddress() else bad)("라이브러리 주소와 일치")

    step("6. 공개키 → Ethereum 주소")
    unc = eth_node.PublicKey().RawUncompressed().ToBytes()[1:]  # 맨 앞 04 제거
    kk = Keccak256.QuickDigest(unc)
    kv("비압축 공개키", unc.hex()[:30] + "… (64바이트)", width=16)
    kv("Keccak-256", kk.hex()[:30] + "…", width=16)
    kv("뒤 20바이트", kk[-20:].hex(), width=16, color="green")
    eth_addr = eth_node.PublicKey().ToAddress()
    (good if eth_addr.lower()[2:] == kk[-20:].hex() else bad)(f"0x… 주소 {eth_addr}  (체크섬 대소문자 적용)")
    say("같은 12단어에서 비트코인과 이더리움 주소가 모두 나온다. 키는 '단어'에서 파생된다.")

    step("7. 복구 · 오타 · 25번째 단어")
    w = wallet(mnemonic)
    again = wallet(mnemonic)
    (good if again == w else bad)(f"같은 12단어 → 같은 지갑 (복구 가능): {w['Ethereum']}")
    alt = mnemonic.split()
    alt[0] = "abandon" if alt[0] != "abandon" else "zoo"
    ok = Bip39MnemonicValidator().IsValid(" ".join(alt))
    print(f"  첫 단어를 '{alt[0]}' 로 바꾼 니모닉: 체크섬 {'유효(다른 지갑이 만들어짐)' if ok else '오류 → 지갑이 거부 (오타 방지)'}")
    pw = wallet(mnemonic, "특강2026")
    print(f"  25번째 단어(passphrase)='특강2026' 추가 → 전혀 다른 지갑: {pw['Ethereum']}")
    say("passphrase 는 12단어가 털려도 자산을 지키는 마지막 비밀번호가 될 수 있다 (잊으면 복구 불가).")

    done("정리: 지갑의 실체는 서버가 아니라 12단어. 단어 → 시드 → 키 → 주소는 모두 결정적(수학)이다.")


if __name__ == "__main__":
    main()
