import hashlib
import time

def mining(difficulty):
    # 정답지 앞에 0이 몇 개 붙어야 하는지 정해요 (난이도)
    target = "0" * difficulty
    nonce = 0 # 0부터 1씩 늘려가며 넣어볼 숫자예요
    
    print(f"채굴 시작! 목표: 앞자리에 0이 {difficulty}개 있어야 함")
    start_time = time.time() # 시작 시간 기록

    while True:
        # '내용 + nonce'를 합쳐서 해시를 만들어요
        content = "철수가 영희에게 1BTC 전송" + str(nonce)
        hash_result = hashlib.sha256(content.encode()).hexdigest()
        
        # 만약 해시값이 목표(000...)로 시작하면 정답!
        if hash_result.startswith(target):
            end_time = time.time()
            print(f"✨ 채굴 성공! 정답 숫자(Nonce): {nonce}")
            print(f"찾아낸 해시: {hash_result}")
            print(f"걸린 시간: {end_time - start_time:.2f}초")
            break
        
        nonce += 1 # 정답이 아니면 숫자를 1 늘려서 다시 시도!

# 난이도 4로 시작해볼까요? (0000 찾기)
mining(6)