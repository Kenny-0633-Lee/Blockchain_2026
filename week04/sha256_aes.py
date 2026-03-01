import hashlib # 암호화를 도와주는 도구 상자를 불러와요

def make_fingerprint(text):
    # 입력받은 글자를 SHA-256이라는 아주 강력한 암호로 바꿔줍니다.
    result = hashlib.sha256(text.encode()).hexdigest()
    return result

# 직접 확인해보기
my_name = "00000"
print(f"[{my_name}]의 디지털 지문: {make_fingerprint(my_name)}")

# 글자 하나만 바꿔보기
my_name_2 = "00100" # 첫 글자를 소문자로 바꿨어요
print(f"[{my_name_2}]의 디지털 지문: {make_fingerprint(my_name_2)}")