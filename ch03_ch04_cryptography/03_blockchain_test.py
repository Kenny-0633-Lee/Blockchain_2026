import hashlib # 자물쇠를 만드는 도구
import json
from datetime import datetime

# 블록체인을 관리하는 기계예요
class Blockchain:
    def __init__(self):
        self.chain = []
        # 1. 제네시스 블록(최초의 블록)을 만들어서 체인에 넣어요
        self.create_block(data="제네시스 블록 (시작)", prev_hash='0')

    def create_block(self, data, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'data': data,
            'prev_hash': prev_hash # 이전 블록의 자물쇠 값을 보관해요!
        }
        # 블록 전체 내용을 해시(자물쇠)로 만듭니다
        block_string = json.dumps(block, sort_keys=True).encode()
        block['hash'] = hashlib.sha256(block_string).hexdigest()
        
        self.chain.append(block)
        return block

# --- 실습 시작 ---
my_coin = Blockchain()

# 2. 두 번째, 세 번째 블록을 줄줄이 엮어요
h1 = my_coin.chain[0]['hash']
my_coin.create_block(data="철수가 영희에게 10코인 전송", prev_hash=h1)

h2 = my_coin.chain[1]['hash']
my_coin.create_block(data="영희가 민수에게 5코인 전송", prev_hash=h2)

# 3. 체인 결과 출력
for block in my_coin.chain:
    print(f"블록 #{block['index']}")
    print(f"내용: {block['data']}")
    
    # print(f"이전 블록의 자물쇠: {block['prev_hash'][:20]}...")
    # print(f"현재 블록의 자물쇠: {block['hash'][:20]}...")
    print(f"이전 블록의 자물쇠: {block['prev_hash']}")
    print(f"현재 블록의 자물쇠: {block['hash']}")
    print("-" * 40)

    # print(block)