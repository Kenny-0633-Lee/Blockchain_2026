import os
import shutil
from pathlib import Path

# 1. 매핑 정의: (기존 경로, 새로운 경로)
# 교수님의 v0.83/v0.74 커리큘럼 기반 매핑입니다.
MAPPING = {
    # 관리 및 설정
    "02_Scripts_Admin/2.1_convert.py": "00_Scripts/2.1_convert.py",
    "02_Scripts_Admin/2.2_distribute.py": "00_Scripts/2.2_distribute.py",
    
    # 주차별 배치 (이론 및 실습 코드)
    "01_Lecture_Notes/00_orientation/00_orientation.pdf": "week01/00_orientation.pdf",
    
    # Cryptography (Week 03-06)
    "ch03_ch04_cryptography/03_blockchain_test.py": "week03/merkle_tree.py",
    "ch03_ch04_cryptography/01_hash_test.py": "week04/sha256_aes.py",
    "ch03_ch04_cryptography/02_signature_test.py": "week05/ecdsa_bip39.py",
    "ch03_ch04_cryptography/05_mining_test.py": "week06/pow_simulator.py",
    
    # Solidity & DApps (Week 10-14)
    "04_Labs_Solidity/contracts/SimpleStorage.sol": "week10/SimpleStorage.sol",
}

def migrate():
    print("🚀 Blockchain_2026 리포지토리 구조 개편을 시작합니다.\n")
    
    root = Path(".")
    
    # 새로운 구조의 기본 디렉토리 생성
    weeks = [f"week{i:02d}" for i in range(1, 16)]
    base_dirs = ["00_Scripts", "assets"] + weeks
    
    for d in base_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        # 각 주차별 README.md가 없는 경우 생성 (템플릿)
        readme = Path(d) / "README.md"
        if not readme.exists():
            with open(readme, "w", encoding="utf-8") as f:
                f.write(f"# {d.capitalize()} \n\n이곳에 강의 자료와 실습 가이드를 업로드하세요.")

    # 파일 이동 및 이름 변경
    for old_path_str, new_path_str in MAPPING.items():
        old_path = root / old_path_str
        new_path = root / new_path_str
        
        if old_path.exists():
            # 목적지 디렉토리 보장
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
            print(f"✅ Moved: {old_path_str} -> {new_path_str}")
        else:
            print(f"⚠️ Skipped: {old_path_str} (파일을 찾을 수 없음)")

    # 환경변수 템플릿 생성
    env_example = root / ".env.example"
    if not env_example.exists():
        with open(env_example, "w") as f:
            f.write("ADMIN_PRIVATE_KEY=your_key_here\nINFURA_API_KEY=your_key_here\n")
            print("✅ Created: .env.example")

    print("\n✨ 구조 개편 완료. 이제 'git add .' 후 커밋하세요.")

if __name__ == "__main__":
    migrate()