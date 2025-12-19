import sys
import os
sys.path.append(os.getcwd())

from database import SessionLocal
from ai.problem_generator import generate_problems_for_weak_areas
import json

def test():
    db = SessionLocal()
    try:
        # 약점 데이터가 없는 가상의 사용자 'new_user'에 대해 문제 생성 요청
        print("Testing problem generation for 'new_user' (no weak points)...")
        problems = generate_problems_for_weak_areas(
            db=db,
            username="new_user",
            subject="문학",
            count=2,
            difficulty="medium"
        )
        
        print(f"Generated {len(problems)} problems:")
        for i, p in enumerate(problems):
            print(f"--- Problem {i+1} ---")
            print(f"Standard Code: {p['standard_code']}")
            print(f"Question: {p['question'][:100]}...")
            
    finally:
        db.close()

if __name__ == "__main__":
    test()
