from ecdsa import SigningKey, SECP256k1

# 1. 개인키(Private Key) 생성: 나만 알고 있어야 하는 비밀번호!
# 비트코인이 사용하는 'SECP256k1'이라는 수학 규칙을 사용합니다.
private_key = SigningKey.generate(curve=SECP256k1)
private_key_hex = private_key.to_string().hex()

# 2. 공개키(Public Key) 생성: 남들에게 알려주는 나의 계좌번호!
# 개인키로부터 수학적으로 계산되어 나옵니다.
public_key = private_key.get_verifying_key()
public_key_hex = public_key.to_string().hex()

print("🔑 [1] 나의 개인키 (절대 비밀!):")
print(private_key_hex)
print("\n🔓 [2] 나의 공개키 (내 계좌번호):")
print(public_key_hex)

# 3. 디지털 서명(Digital Signature) 실습
# "나는 누구에게 1 BTC를 보냅니다"라는 편지에 도장을 찍어볼까요?
message = "I send 1 BTC to my friend."
message_bytes = message.encode()

# 개인키를 이용해 메시지에 도장(서명)을 찍습니다.
signature = private_key.sign(message_bytes)

print("\n✍️ [3] 디지털 서명 (메시지에 찍힌 도장):")
print(signature.hex())

# 4. 검증(Verification)
# 남들이 내 공개키를 이용해 이 도장이 진짜인지 확인합니다.
try:
    is_valid = public_key.verify(signature, message_bytes)
    print("\n✅ [4] 검증 결과: 진짜 주인이 보낸 거래가 맞습니다!")
except:
    print("\n❌ [4] 검증 결과: 도장이 가짜이거나 내용이 바뀌었습니다!")