from mnemonic import Mnemonic

# 1. 영어 단어장을 준비합니다
mnemo = Mnemonic("english")

# 2. 지갑의 씨앗이 될 12개 단어를 무작위로 뽑아요
words = mnemo.generate(strength=128) 

print("🌟 내 지갑을 지켜주는 12개 마법 단어:")
print("-" * 50)
print(words)
print("-" * 50)

# 3. 이 단어들을 아주 긴 숫자(시드)로 바꿔서 지갑 주소를 만들 준비를 해요
seed = mnemo.to_seed(words)
print("\n🔑 이 단어들이 숫자로 바뀌면 이렇게 길어져요 (복구용 마스터키):")
print(seed.hex())