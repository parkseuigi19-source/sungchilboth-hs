"""
대시보드 API
학생 성취도 대시보드 및 히트맵 데이터 제공
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine
from models import Base
from ai.dashboard_analyzer import analyze_student_achievement, generate_heatmap_data
from pydantic import BaseModel


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


class DashboardRequest(BaseModel):
    username: str
    subject: str = "국어"


@router.get("")
def get_dashboard(username: str, subject: str = "국어", db: Session = Depends(get_db)):
    """
    학생 대시보드 기본 정보 조회 (GET 방식)
    
    Args:
        username: 학생 아이디
        subject: 과목 (기본값: 국어)
        db: 데이터베이스 세션
    
    Returns:
        대시보드 상세 정보 (성취도 분석 포함)
    """
    try:
        # 성취도 분석 데이터 생성
        dashboard_data = analyze_student_achievement(
            db=db,
            username=username,
            subject=subject
        )
        
        # 프론트엔드가 기대하는 형식으로 데이터 변환
        achievement_scores = {}
        for code, data in dashboard_data.get("achievement_by_standard", {}).items():
            achievement_scores[code] = data["average_score"]
        
        
        return {
            "success": True,
            "username": username,
            "subject": subject,
            "achievement_scores": achievement_scores,
            "total_questions": dashboard_data["overall_stats"]["total_questions"],
            "average_score": dashboard_data["overall_stats"]["average_score"],
            "study_days": 0,  # TODO: 실제 학습 일수 계산 로직 추가
            "strong_areas": dashboard_data.get("strong_areas", []),
            "weak_points": [],
            "recommended_areas": [],
            "message": "대시보드 데이터 조회 성공"
        }
    except Exception as e:
        # 오류 발생 시 기본 데이터 반환
        print(f"Dashboard Error: {str(e)}")
        return {
            "success": True,
            "username": username,
            "subject": subject,
            "achievement_scores": {},
            "total_questions": 0,
            "average_score": 0,
            "study_days": 0,
            "strong_areas": [],
            "weak_points": [],
            "recommended_areas": [],
            "message": "데이터가 없습니다"
        }


@router.post("/achievement")
def get_achievement_dashboard(request: DashboardRequest, db: Session = Depends(get_db)):
    """
    학생 성취도 대시보드 데이터 조회
    
    Args:
        request: 요청 데이터 (username, subject)
        db: 데이터베이스 세션
    
    Returns:
        성취도 대시보드 데이터
    """
    try:
        dashboard_data = analyze_student_achievement(
            db=db,
            username=request.username,
            subject=request.subject
        )
        return {"success": True, "data": dashboard_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 생성 실패: {str(e)}")


@router.post("/heatmap")
def get_heatmap(request: DashboardRequest, db: Session = Depends(get_db)):
    """
    강약점 히트맵 데이터 조회
    
    Args:
        request: 요청 데이터 (username, subject)
        db: 데이터베이스 세션
    
    Returns:
        히트맵 데이터
    """
    try:
        heatmap_data = generate_heatmap_data(
            db=db,
            username=request.username,
            subject=request.subject
        )
        return {"success": True, "data": heatmap_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히트맵 데이터 생성 실패: {str(e)}")
