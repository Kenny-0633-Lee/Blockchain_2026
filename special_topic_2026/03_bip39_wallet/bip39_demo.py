"""
03_bip39_wallet/bip39_demo.py  (특강 2026-11-25)
================================================
BIP-39 니모닉 -> 시드 -> 개인키 -> 공개키 -> 주소 (Bitcoin / Ethereum)

보여줄 것
  1) 엔트로피 128bit + 체크섬 4bit -> 단어 12개
  2) PBKDF2-HMAC-SHA512 (2048회) 로 시드 만들기
  3) 시드 -> BIP-44 경로 -> Bitcoin, Ethereum 주소
  4) 같은 단어 = 같은 지갑 (복구) / 단어 하나만 달라도 완전히 다른 지갑
  5) 단어 순서를 바꾸면 체크섬이 막아 준다

실행 (macOS 터미널 / Windows PowerShell·Git Bash 공통, 저장소 루트에서)
  uv run python special_topic_2026/03_bip39_wallet/bip39_demo.py

교육용입니다. 여기서 만든 니모닉에 실제 자산을 넣지 마세요.
"""
import hashlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from bip_utils import (Bip39Languages, Bip39MnemonicGenerator, Bip39MnemonicValidator,
                           Bip39SeedGenerator, Bip39WordsNum, Bip44, Bip44Changes, Bip44Coins)
except ImportError:
    print("패키지 필요: uv sync  (또는 pip install bip-utils)")
    sys.exit(1)


def wallet_from(mnemonic: str, passphrase: str = ""):
    seed = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    out = {"seed": seed.hex()}
    for name, coin in [("Bitcoin", Bip44Coins.BITCOIN), ("Ethereum", Bip44Coins.ETHEREUM)]:
        acct = (Bip44.FromSeed(seed, coin).Purpose().Coin().Account(0)
                .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0))
        out[name] = (acct.PublicKey().ToAddress(), acct.PrivateKey().Raw().ToHex())
    return out


def main():
    print("[1] 엔트로피 -> 니모닉")
    mn = str(Bip39MnemonicGenerator(Bip39Languages.ENGLISH).FromWordsNumber(Bip39WordsNum.WORDS_NUM_12))
    print(f"  니모닉(12단어): {mn}")
    print("  128bit 엔트로피 + 4bit 체크섬 = 132bit = 11bit x 12단어 (단어장 2048개 = 2^11)")

    print("\n[2] 시드: PBKDF2-HMAC-SHA512(니모닉, 'mnemonic'+passphrase, 2048회)")
    w = wallet_from(mn)
    manual = hashlib.pbkdf2_hmac("sha512", mn.encode(), b"mnemonic", 2048).hex()
    print(f"  라이브러리 시드 : {w['seed'][:48]}…")
    print(f"  직접 계산한 시드: {manual[:48]}…  일치: {manual == w['seed']}")

    print("\n[3] 시드 -> BIP-44 (m/44'/coin'/0'/0/0) -> 주소")
    for name in ("Bitcoin", "Ethereum"):
        addr, priv = w[name]
        print(f"  {name:<8} 주소 {addr}")
        print(f"  {'':<8} 개인키 {priv[:16]}… (공개 금지)")

    print("\n[4] 복구와 민감도")
    again = wallet_from(mn)
    print(f"  같은 니모닉 -> 같은 주소: {again['Ethereum'][0] == w['Ethereum'][0]}")
    words = mn.split()
    alt_words = words[:]
    alt_words[0] = "abandon" if words[0] != "abandon" else "zoo"
    alt = " ".join(alt_words)
    ok = Bip39MnemonicValidator().IsValid(alt)
    print(f"  첫 단어만 바꾼 니모닉의 체크섬 유효 여부: {ok}")
    if ok:
        print(f"    -> 유효해서 전혀 다른 주소가 나온다: {wallet_from(alt)['Ethereum'][0]}")
    else:
        print("    -> 체크섬이 틀려서 지갑이 거부한다 (오타 방지)")
    pw = wallet_from(mn, passphrase="특강2026")
    print(f"  25번째 단어(passphrase) 추가 -> 다른 지갑: {pw['Ethereum'][0]}")

    print("\n[5] 단어 순서를 바꾸면?")
    shuffled = " ".join(words[::-1])
    print(f"  역순 니모닉 유효 여부: {Bip39MnemonicValidator().IsValid(shuffled)} (대부분 체크섬에서 걸린다)")
    print("\n정리: 지갑의 실체는 '12단어'. 서버가 아니라 이 단어를 가진 사람이 자산의 주인이다.")


if __name__ == "__main__":
    main()
