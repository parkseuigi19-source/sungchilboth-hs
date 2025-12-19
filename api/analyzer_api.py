from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
import os
from database import engine
from sqlalchemy.orm import Session
from models import Record, AchievementRecord
from ai.standards_matcher import matcher

router = APIRouter(prefix="/api/student", tags=["Analyzer"])

# ============================================
# ✅ 피드백 & 점수 생성 함수
# ============================================
def generate_feedback(std_domain: str):
    """성취기준 도메인에 따른 피드백 및 점수 생성"""
    std_domain = std_domain.strip()

    if std_domain == "화법" or std_domain == "듣기·말하기":
        return 85, "공감적 듣기나 명확한 말하기 전략을 구체적으로 서술해 보세요."
    elif std_domain == "문법":
        return 90, "문법 개념을 정의하고 예문을 통해 설명하면 좋아요."
    elif std_domain == "독서" or std_domain == "읽기":
        return 80, "글의 핵심 내용과 필자의 의도를 명확히 구분해 보세요."
    elif std_domain == "문학":
        return 95, "작품의 주제와 인물의 관계를 구체적인 근거로 제시해 보세요."
    elif std_domain == "작문" or std_domain == "쓰기":
        return 88, "글의 구조를 명확히 하고 예시나 근거를 들어 설득력을 높이세요."
    else:
        return 70, "핵심 개념을 중심으로 논리적으로 정리해 보세요."


# ============================================
# ✅ 학생 서술형 분석 API
# ============================================
@router.post("/analyze")
async def analyze(request: Request):
    """
    서술형 답안 분석 (성취기준 자동 매칭 + 점수 + 피드백 반환)
    """
    data = await request.json()
    question = data.get("question", "")
    essay = data.get("essay", "")

    # 1️⃣ AI 성취기준 매칭 (고도화됨)
    std = matcher.match(question, essay)

    # 2️⃣ 점수 및 피드백 생성
    score, feedback = generate_feedback(std["domain"])

    # 3️⃣ 데이터베이스 저장
    try:
        db = Session(bind=engine)
        username = data.get("username", "anonymous")
        
        # 교사용 대시보드 및 일반 기록용
        new_record = Record(
            username=username,
            question=question,
            reply=feedback,
            category=f"분석-{std['domain']}",
            score=float(score)
        )
        db.add(new_record)
        
        # 성취도 통계용
        new_ach = AchievementRecord(
            username=username,
            subject=std["domain"],
            standard_code=std["code"],
            score=float(score)
        )
        db.add(new_ach)
        
        db.commit()
        db.close()
    except Exception as db_err:
        print(f"분석 기록 저장 오류: {db_err}")

    # 4️⃣ 결과 반환 (프론트엔드 접근 구조 통일)
    return JSONResponse({
        "related_standard": {
            "id": std["code"],
            "domain": std["domain"],
            "title": std["desc"]
        },
        "score": score,
        "feedback": feedback,
        "teacher_tips": f"{std['domain']} 영역 학습을 강화해보세요! ({std['desc']})"
    })
