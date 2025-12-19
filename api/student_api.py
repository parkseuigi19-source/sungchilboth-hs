# api/student_api.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json

from database import get_db
from models import User, Submission, Feedback, MasteryLevel, Question, Record
from ai.core.graph import app_graph

router = APIRouter(prefix="/api/student", tags=["Student"])

@router.post("/submit")
async def submit_answer(request: Request, db: Session = Depends(get_db)):
    """
    학생 답안 제출 및 AI 분석 (Graph 기반)
    """
    data = await request.json()
    username = data.get("username", "학생1")
    question_id = data.get("question_id", 1)
    answer_text = data.get("answer_text", "").strip()

    if not answer_text:
        return JSONResponse({"success": False, "msg": "답안을 입력해주세요."}, status_code=400)

    # 1. 문제 정보 조회 (Mock or DB)
    # 실제 구현에서는 DB에서 문제를 조회해야 함
    question_content = "다음은 김소월의 시 '진달래꽃'의 일부이다. 이 시에 나타난 화자의 태도를 '이별의 정한'과 관련지어 200자 내외로 서술하시오."
    standard_content = "문학 작품에 드러난 작가의 개성을 이해하고 작품을 감상한다."
    rubric_content = "1. 화자의 태도(애이불비)가 잘 드러났는가? (5점)\n2. '이별의 정한' 개념을 포함했는가? (3점)\n3. 문장이 자연스러운가? (2점)"

    # 2. AI Graph 실행
    inputs = {
        "question": question_content,
        "standard": standard_content,
        "rubric": rubric_content,
        "student_answer": answer_text,
        "analysis_result": {},
        "mastery_level": "FAIL",
        "feedback_text": ""
    }

    try:
        # LangGraph 실행
        final_state = await app_graph.ainvoke(inputs)
        
        analysis = final_state.get("analysis_result", {})
        mastery = final_state.get("mastery_level", "FAIL")
        feedback_text = final_state.get("feedback_text", "피드백을 생성하지 못했습니다.")
        recommendations = final_state.get("recommendations", [])

        # 3. DB 저장
        # - User 조회 (없으면 임시 생성)
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username, name=username, role="student")
            db.add(user)
            db.commit()
            db.refresh(user)

        # - Submission 저장
        submission = Submission(
            question_id=question_id,
            student_id=user.id,
            answer_text=answer_text,
            submitted_at=datetime.now()
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # - Feedback 저장
        feedback_rec = Feedback(
            submission_id=submission.id,
            mastery_level=MasteryLevel(mastery) if mastery in ["PASS", "PARTIAL", "FAIL"] else MasteryLevel.FAIL,
            overall_comment=feedback_text,
            teacher_summary=json.dumps(analysis, ensure_ascii=False),
            analysis_json=analysis,
            misconceptions=[] # TODO: 추출 로직 추가
        )
        db.add(feedback_rec)
        db.commit()
        db.refresh(feedback_rec)

        db.commit()

        return JSONResponse({
            "success": True,
            "feedback": feedback_text,
            "analysis": analysis,
            "recommendations": recommendations
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "msg": f"AI 분석 중 오류 발생: {str(e)}"}, status_code=500)

@router.get("/history")
async def get_history(username: str, db: Session = Depends(get_db)):
    """학생의 제출 이력 조회"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {"history": []}
    
    submissions = db.query(Submission).filter(Submission.student_id == user.id).order_by(Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        fb = sub.feedback
        result.append({
            "id": sub.id,
            "question_id": sub.question_id,
            "answer": sub.answer_text,
            "submitted_at": sub.submitted_at.isoformat(),
            "feedback": fb.overall_comment if fb else None,
            "mastery": fb.mastery_level if fb else None
        })
    
    return {"history": result}


