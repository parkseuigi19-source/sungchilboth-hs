"""
서술형 자동 채점 모듈
GPT-4 기반 서술형/논술형 답안 채점 및 피드백 생성
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from models import EssayGrading
from openai import OpenAI
from config import settings
import json


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def grade_essay(
    db: Session,
    username: str,
    subject: str,
    question: str,
    student_answer: str,
    model_answer: str = None,
    max_score: int = 100
) -> Dict[str, Any]:
    """
    서술형 답안 자동 채점
    
    Args:
        db: 데이터베이스 세션
        username: 학생 사용자명
        subject: 과목
        question: 문제
        student_answer: 학생 답안
        model_answer: 모범 답안 (선택)
        max_score: 만점
    
    Returns:
        채점 결과
    """
    # GPT-4를 사용하여 채점
    grading_result = grade_with_gpt(
        question=question,
        student_answer=student_answer,
        model_answer=model_answer,
        max_score=max_score
    )
    
    # 데이터베이스에 저장
    new_grading = EssayGrading(
        username=username,
        subject=subject,
        question=question,
        student_answer=student_answer,
        model_answer=model_answer or "모범답안 없음",
        score=grading_result["score"],
        grading_reason=grading_result["reason"],
        feedback=grading_result["feedback"],
        graded_by="AI"
    )
    db.add(new_grading)
    db.commit()
    db.refresh(new_grading)
    
    return {
        "id": new_grading.id,
        "score": grading_result["score"],
        "max_score": max_score,
        "percentage": round((grading_result["score"] / max_score) * 100, 2),
        "reason": grading_result["reason"],
        "feedback": grading_result["feedback"],
        "graded_at": new_grading.created_at.isoformat()
    }


def grade_with_gpt(
    question: str,
    student_answer: str,
    model_answer: str = None,
    max_score: int = 100
) -> Dict[str, Any]:
    """
    GPT-4를 사용하여 답안 채점
    
    Args:
        question: 문제
        student_answer: 학생 답안
        model_answer: 모범 답안
        max_score: 만점
    
    Returns:
        채점 결과 (점수, 근거, 피드백)
    """
    model_answer_section = f"\n**모범 답안**:\n{model_answer}" if model_answer else ""
    
    prompt = f"""
당신은 고등학교 국어 교사입니다. 다음 서술형 문제에 대한 학생의 답안을 채점해주세요.

**문제**:
{question}
{model_answer_section}

**학생 답안**:
{student_answer}

**채점 기준**:
1. 내용의 정확성 (40%)
2. 논리적 구성 (30%)
3. 표현의 적절성 (20%)
4. 창의성 및 심화 (10%)

다음 형식의 JSON으로 채점 결과를 작성해주세요:
{{
  "score": 점수 (0-{max_score}),
  "reason": "채점 근거 (각 기준별로 어떻게 평가했는지 구체적으로)",
  "feedback": "개선을 위한 피드백 (학생이 어떤 부분을 보완하면 좋을지)"
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 공정하고 세심한 교육 평가 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 일관성을 위해 낮은 temperature
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return {
            "score": min(max_score, max(0, result.get("score", 0))),
            "reason": result.get("reason", "채점 근거를 생성할 수 없습니다."),
            "feedback": result.get("feedback", "피드백을 생성할 수 없습니다.")
        }
        
    except Exception as e:
        print(f"채점 중 오류 발생: {e}")
        # 기본 채점 결과 반환
        return {
            "score": max_score // 2,
            "reason": "자동 채점에 실패하여 기본 점수가 부여되었습니다.",
            "feedback": "교사의 직접 채점이 필요합니다."
        }


def get_grading_history(db: Session, username: str, subject: str = None, limit: int = 10) -> list:
    """
    학생의 채점 이력 조회
    
    Args:
        db: 데이터베이스 세션
        username: 학생 사용자명
        subject: 과목 (선택)
        limit: 조회 개수
    
    Returns:
        채점 이력 리스트
    """
    query = db.query(EssayGrading).filter(EssayGrading.username == username)
    
    if subject:
        query = query.filter(EssayGrading.subject == subject)
    
    gradings = query.order_by(EssayGrading.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": g.id,
            "subject": g.subject,
            "question": g.question[:100] + "..." if len(g.question) > 100 else g.question,
            "score": g.score,
            "graded_by": g.graded_by,
            "created_at": g.created_at.isoformat()
        }
        for g in gradings
    ]


def get_grading_detail(db: Session, grading_id: int) -> Dict[str, Any]:
    """
    채점 상세 정보 조회
    
    Args:
        db: 데이터베이스 세션
        grading_id: 채점 ID
    
    Returns:
        채점 상세 정보
    """
    grading = db.query(EssayGrading).filter(EssayGrading.id == grading_id).first()
    
    if not grading:
        return None
    
    return {
        "id": grading.id,
        "username": grading.username,
        "subject": grading.subject,
        "question": grading.question,
        "student_answer": grading.student_answer,
        "model_answer": grading.model_answer,
        "score": grading.score,
        "grading_reason": grading.grading_reason,
        "feedback": grading.feedback,
        "graded_by": grading.graded_by,
        "created_at": grading.created_at.isoformat()
    }
