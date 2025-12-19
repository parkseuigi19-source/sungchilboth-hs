"""
데이터베이스 시드 데이터 생성 스크립트
초기 사용자, 학습 기록, 성취도 데이터 등을 생성합니다.
"""
from sqlalchemy.orm import Session
from database import engine, get_db
from models import (
    Base, User, UserRole, Class, ClassMember, Record, 
    Question, Submission, Feedback, MasteryLevel, 
    AchievementRecord, EssayGrading,
    ClassReport
)
from datetime import datetime, timedelta
import random
import os

# DB 테이블 생성 (기존 데이터 초기화)
try:
    Base.metadata.drop_all(bind=engine)
    print("[INFO] Existing tables dropped.")
except Exception as e:
    print(f"[WARN] Could not drop tables: {e}")

Base.metadata.create_all(bind=engine)

def seed_data():
    db = Session(bind=engine)
    try:
        print("[INFO] DB Seeding Started...")

        # 1. 교사 생성
        teacher = db.query(User).filter(User.username == "teacher1").first()
        if not teacher:
            teacher = User(
                username="teacher1",
                password_hash="1234", # 비밀번호 설정
                name="김선생",
                role=UserRole.TEACHER,
                email="teacher@school.com"
            )
            db.add(teacher)
            db.commit()
            print("[OK] Teacher account created (ID: teacher1 / PW: 1234)")
        else:
            print("[INFO] Teacher account 'teacher1' already exists.")
        
        # 2. 반 생성
        classes = ["1학년 1반", "1학년 2반", "1학년 3반"]
        class_objs = []
        for c_name in classes:
            cls = Class(name=c_name, teacher_id=teacher.id, grade=1, year=2024)
            db.add(cls)
            class_objs.append(cls)
        db.commit()
        
        # 3. 학생 및 성취도 데이터 생성
        korean_names = ["김철수", "이영희", "박민수", "정수민", "최지우", "강동원", "송혜교", "현빈", "손예진", "유재석",
                        "박보검", "김유정", "차은우", "아이유", "bts", "봉준호", "손흥민", "김연아", "페이커", "뉴진스"]
        
        students = []
        for i, name in enumerate(korean_names):
            username = f"student{i+1}"
            existing_student = db.query(User).filter(User.username == username).first()
            if existing_student:
                students.append(existing_student)
                continue

            student = User(
                username=username,
                password_hash="1234", # 비밀번호 설정
                name=name,
                role=UserRole.STUDENT
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
            # 반 배정
            cls = class_objs[i % len(class_objs)]
            member = ClassMember(class_id=cls.id, student_id=student.id)
            db.add(member)
            
            students.append(student)

            # 성취도 기록 (AchievementRecord) -> 차트용
            subjects = ["문학", "독서", "화법", "작문", "문법"]
            for subj in subjects:
                # 랜덤으로 0~100점
                base_score = random.randint(50, 90)
                score = min(100, base_score + random.randint(-10, 10))
                
                record = AchievementRecord(
                    username=student.username,
                    subject=subj,
                    standard_code=f"K-HS-{subj[:2]}01",
                    score=score,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(record)
        
        db.commit()
        print(f"[OK] Created {len(students)} students and achievement records")

        # 4. 최근 질문 (Record) -> 대시보드 '최근 학생 질문'
        questions = [
            "진달래꽃의 주제가 뭐야?",
            "은유법과 직유법의 차이점 알려줘",
            "비판적 읽기가 왜 중요해?",
            "설명문의 특징이 궁금해",
            "관동별곡 해석 좀 도와줘",
            "단어의 형성 방법 알려줘",
            "음운 변동 현상이 헷갈려"
        ]
        
        for _ in range(15):
            stu = random.choice(students)
            q_text = random.choice(questions)
            rec = Record(
                username=stu.username,
                question=q_text,
                reply="AI 답변입니다...",
                category="질문",
                created_at=datetime.now() - timedelta(minutes=random.randint(5, 300))
            )
            db.add(rec)
        db.commit()
        print("[OK] Created recent questions")
        
        print("[SUCCESS] All seed data created successfully!")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
