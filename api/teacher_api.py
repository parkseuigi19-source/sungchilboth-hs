"""
교사용 API
학생 관리, 성취도 분석, AI 비서, 학급 리포트, 문항 관리 등
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine
from models import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# AI 모듈 임포트
from ai.teacher_assistant import (
    summarize_student_questions,
    analyze_wrong_answer_patterns,
    generate_teaching_advice
)
from ai.class_report_generator import generate_class_report, get_class_report
from ai.essay_grader import grade_essay
from ai.class_report_generator import generate_class_report, get_class_report
from ai.essay_grader import grade_essay


router = APIRouter(prefix="/api/teacher", tags=["Teacher"])


def get_db():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


# ==================== AI 비서 ====================

class QuestionSummaryRequest(BaseModel):
    teacher_username: str
    subject: str = "국어"
    days: int = 7


class WrongAnswerAnalysisRequest(BaseModel):
    teacher_username: str
    subject: str = "국어"


class TeachingAdviceRequest(BaseModel):
    teacher_username: str
    topic: str
    subject: str = "국어"


@router.post("/assistant/summarize-questions")
def summarize_questions(request: QuestionSummaryRequest, db: Session = Depends(get_db)):
    """학생 질문 요약 및 분석"""
    try:
        result = summarize_student_questions(
            db=db,
            teacher_username=request.teacher_username,
            subject=request.subject,
            days=request.days
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 요약 실패: {str(e)}")


@router.post("/assistant/analyze-wrong-answers")
def analyze_wrong_answers(request: WrongAnswerAnalysisRequest, db: Session = Depends(get_db)):
    """오답 유형 분석"""
    try:
        result = analyze_wrong_answer_patterns(
            db=db,
            teacher_username=request.teacher_username,
            subject=request.subject
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오답 분석 실패: {str(e)}")


@router.post("/assistant/teaching-advice")
def get_teaching_advice(request: TeachingAdviceRequest, db: Session = Depends(get_db)):
    """수업자료 조언 생성"""
    try:
        result = generate_teaching_advice(
            db=db,
            teacher_username=request.teacher_username,
            topic=request.topic,
            subject=request.subject
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조언 생성 실패: {str(e)}")


# ==================== 학급 리포트 ====================

class ClassReportRequest(BaseModel):
    teacher_username: str
    class_name: str
    subject: str = "국어"
    report_type: str = "unit"
    student_list: Optional[List[str]] = None


@router.post("/class-report/generate")
def create_class_report(request: ClassReportRequest, db: Session = Depends(get_db)):
    """학급 성취도 리포트 생성"""
    try:
        result = generate_class_report(
            db=db,
            teacher_username=request.teacher_username,
            class_name=request.class_name,
            subject=request.subject,
            report_type=request.report_type,
            student_list=request.student_list
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 생성 실패: {str(e)}")


@router.get("/class-report/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """학급 리포트 조회"""
    try:
        result = get_class_report(db=db, report_id=report_id)
        
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "리포트를 찾을 수 없습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 조회 실패: {str(e)}")


@router.get("/class-report/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    """학급 리포트 다운로드 데이터 조회"""
    try:
        result = get_class_report(db=db, report_id=report_id)
        if result:
            return {"success": True, "pdf_path": result.get("pdf_path")}
        else:
            raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"다운로드 정보 조회 실패: {str(e)}")


@router.get("/class-report/list")
def list_class_reports(teacher_username: str = "teacher1", db: Session = Depends(get_db)):
    """학급 리포트 목록 조회"""
    try:
        from models import ClassReport
        reports = db.query(ClassReport).filter(
            ClassReport.teacher_username == teacher_username
        ).order_by(ClassReport.created_at.desc()).all()
        
        return {
            "success": True, 
            "data": [
                {
                    "id": r.id,
                    "class_name": r.class_name,
                    "subject": r.subject,
                    "report_type": r.report_type,
                    "total_students": r.total_students,
                    "average_score": r.average_score,
                    "created_at": r.created_at.isoformat()
                } for r in reports
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 목록 조회 실패: {str(e)}")


# ==================== 자동 채점 ====================

class AutoGradeRequest(BaseModel):
    username: str
    subject: str
    question: str
    student_answer: str
    model_answer: Optional[str] = None
    max_score: int = 100


@router.post("/auto-grade")
def auto_grade(request: AutoGradeRequest, db: Session = Depends(get_db)):
    """서술형 답안 자동 채점"""
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
        raise HTTPException(status_code=500, detail=f"자동 채점 실패: {str(e)}")


# ==================== 대시보드 통계 ====================

@router.get("/dashboard-stats")
def get_dashboard_stats(teacher_username: str = "teacher1", db: Session = Depends(get_db)):
    """교사 대시보드용 통계 데이터"""
    try:
        from models import Record, Submission, Feedback, Class, ClassMember, AchievementRecord, User
        from sqlalchemy import func
        from datetime import datetime
        
        # 1. 최근 학생 질문 (최근 5건)
        recent_questions = db.query(Record).filter(
            Record.question != None
        ).order_by(Record.created_at.desc()).limit(5).all()
        
        questions_data = []
        for q in recent_questions:
            # 시간 포맷팅 (예: 10분 전, 1시간 전)
            diff = datetime.now() - q.created_at
            if diff.days > 0:
                time_str = f"{diff.days}일 전"
            elif diff.seconds >= 3600:
                time_str = f"{diff.seconds // 3600}시간 전"
            else:
                time_str = f"{diff.seconds // 60}분 전"

            questions_data.append({
                "student": q.username, # 실제로는 User 테이블 조인해서 이름 가져오면 더 좋음
                "subject": q.category, # category를 과목/주제로 활용
                "question": q.question,
                "time": time_str
            })

        # 2. 채점 대기 (Feedback이 없는 Submission)
        pending_subs = db.query(Submission).outerjoin(Feedback).filter(
            Feedback.id == None
        ).order_by(Submission.submitted_at.desc()).limit(5).all()
        
        pending_data = []
        for sub in pending_subs:
            # 학생 이름 조회
            student_name = sub.student.name if sub.student else sub.student_id
            
            diff = datetime.now() - sub.submitted_at
            if diff.days > 0:
                time_str = f"{diff.days}일 전"
            elif diff.seconds >= 3600:
                time_str = f"{diff.seconds // 3600}시간 전"
            else:
                time_str = f"{diff.seconds // 60}분 전"
            
            pending_data.append({
                "student": student_name,
                "subject": "서술형", # Submission에 subject 필드가 없어서 고정하거나 question에서 유추
                "submitted": time_str
            })

        # 3. 학급별 성취도 (Class -> Student -> AchievementRecord)
        # 교사가 담당하는 반 조회
        teacher = db.query(User).filter(User.username == teacher_username).first()
        teacher_id = teacher.id if teacher else 1
        
        classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
        
        class_labels = []
        class_scores = []
        
        for cls in classes:
            # 해당 반의 학생들 조회
            students = db.query(User).join(ClassMember).filter(ClassMember.class_id == cls.id).all()
            student_names = [s.username for s in students]
            
            if not student_names:
                avg_score = 0
            else:
                # 학생들의 성취도 평균 계산
                score_res = db.query(func.avg(AchievementRecord.score)).filter(
                    AchievementRecord.username.in_(student_names)
                ).scalar()
                avg_score = round(score_res, 1) if score_res else 0
            
            class_labels.append(cls.name)
            class_scores.append(avg_score)
            
        # 만약 데이터가 없으면 더미 데이터 (시각화 확인용)
        if not class_labels:
            class_labels = ["1반", "2반", "3반"]
            class_scores = [0, 0, 0]

        return {
            "success": True,
            "questions": questions_data,
            "pending": pending_data,
            "chart": {
                "labels": class_labels,
                "data": class_scores
            }
        }

    except Exception as e:
        print(f"대시보드 통계 오류: {e}")
        return {
            "success": False, 
            "message": str(e),
            "questions": [],
            "pending": [],
            "chart": {"labels": [], "data": []}
        }
