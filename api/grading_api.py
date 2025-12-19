"""
채점 API
서술형 답안 자동 채점 및 이력 조회
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine
from models import Base
from ai.essay_grader import grade_essay, get_grading_history, get_grading_detail
from models import Record
from pydantic import BaseModel
from typing import Optional


router = APIRouter(prefix="/api/grading", tags=["Grading"])


def get_db():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


class GradeEssayRequest(BaseModel):
    username: str
    subject: str
    question: str
    student_answer: str
    model_answer: Optional[str] = None
    max_score: int = 100


class GradingHistoryRequest(BaseModel):
    username: str
    subject: Optional[str] = None
    limit: int = 10


@router.post("/essay")
def grade_essay_endpoint(request: GradeEssayRequest, db: Session = Depends(get_db)):
    """
    서술형 답안 자동 채점
    
    Args:
        request: 요청 데이터
        db: 데이터베이스 세션
    
    Returns:
        채점 결과
    """
    try:
        result = grade_essay(
            db=db,
            username=request.username,
            subject=request.subject,
            question=request.question,
            student_answer=request.student_answer,
            model_answer=request.model_answer,
            max_score=request.max_score
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채점 실패: {str(e)}")


@router.post("/history")
def get_history(request: GradingHistoryRequest, db: Session = Depends(get_db)):
    """
    채점 및 활동 통합 이력 조회
    """
    try:
        # 1. 채점 이력 가져오기
        gradings = get_grading_history(
            db=db,
            username=request.username,
            subject=request.subject,
            limit=request.limit
        )
        
        # 2. 채팅 및 분석 기록 가져오기 (Record 테이블)
        records = db.query(Record).filter(
            Record.username == request.username
        ).order_by(Record.created_at.desc()).limit(request.limit).all()
        
        # 3. 데이터 통합
        combined = []
        for g in gradings:
            combined.append({
                "id": g["id"],
                "type": "grading",
                "title": f"[{g['subject']}] 서술형 채점",
                "content": g["question"],
                "score": g["score"],
                "time": g["created_at"]
            })
            
        for r in records:
            time_val = r.created_at.isoformat() if r.created_at else "2025-01-01T00:00:00"
            combined.append({
                "id": r.id,
                "type": "chat" if r.category == "AI 채팅" else "analysis",
                "title": f"[{r.category}] 활동",
                "content": r.question,
                "score": r.score,
                "time": time_val
            })
            
        # 최신순 정렬
        combined.sort(key=lambda x: x["time"], reverse=True)
        
        return {"success": True, "data": combined[:request.limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력 조회 실패: {str(e)}")


@router.get("/detail/{grading_id}")
def get_detail(grading_id: int, db: Session = Depends(get_db)):
    """
    채점 상세 정보 조회
    
    Args:
        grading_id: 채점 ID
        db: 데이터베이스 세션
    
    Returns:
        채점 상세 정보
    """
    try:
        detail = get_grading_detail(db=db, grading_id=grading_id)
        
        if detail:
            return {"success": True, "data": detail}
        else:
            return {"success": False, "message": "채점 정보를 찾을 수 없습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상세 정보 조회 실패: {str(e)}")
