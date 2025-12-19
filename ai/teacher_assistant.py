"""
교사 AI 비서 (Teacher-AI Agent)
학생 질문 요약, 오답 유형 분석, 수업자료 조언 생성
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Record, Submission, Feedback, MasteryLevel, Question
from openai import OpenAI
from config import settings
import json


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize_student_questions(
    db: Session,
    teacher_username: str,
    subject: str = "국어",
    days: int = 7
) -> Dict[str, Any]:
    """
    학생 질문 요약 및 분석
    
    Args:
        db: 데이터베이스 세션
        teacher_username: 교사 사용자명
        subject: 과목
        days: 분석 기간 (일)
    
    Returns:
        질문 요약 및 분석 결과
    """
    from datetime import datetime, timedelta
    
    # 최근 N일간의 학생 질문 조회
    since_date = datetime.now() - timedelta(days=days)
    
    questions = db.query(Record).filter(
        and_(
            Record.created_at >= since_date,
            Record.question != None
        )
    ).all()
    
    if not questions:
        return {
            "message": "분석할 질문이 없습니다.",
            "question_count": 0
        }
    
    # 질문 텍스트 수집
    question_texts = [q.question for q in questions if q.question]
    
    # GPT-4로 질문 요약 및 패턴 분석
    summary = analyze_questions_with_gpt(question_texts, subject)
    
    return {
        "period": f"최근 {days}일",
        "question_count": len(question_texts),
        "summary": summary.get("summary", ""),
        "common_topics": summary.get("common_topics", []),
        "difficulty_areas": summary.get("difficulty_areas", []),
        "teaching_suggestions": summary.get("teaching_suggestions", [])
    }


def analyze_wrong_answer_patterns(
    db: Session,
    teacher_username: str,
    subject: str = "국어"
) -> Dict[str, Any]:
    """
    오답 유형 분석
    
    Args:
        db: 데이터베이스 세션
        teacher_username: 교사 사용자명
        subject: 과목
    
    Returns:
        오답 패턴 분석 결과
    """
    # 낮은 점수의 답안들 조회 (FAIL or PARTIAL)
    wrong_submissions = db.query(Submission).join(Feedback).filter(
        Feedback.mastery_level.in_([MasteryLevel.FAIL, MasteryLevel.PARTIAL])
    ).limit(50).all()
    
    if not wrong_submissions:
        return {
            "message": "분석할 오답이 없습니다.",
            "essay_count": 0
        }
    
    # 오답 데이터 수집
    wrong_answers = []
    for sub in wrong_submissions:
        q_text = sub.question.content if sub.question else "질문 내용 없음"
        wrong_answers.append({
            "question": q_text,
            "student_answer": sub.answer_text,
            "score": sub.feedback.mastery_level if sub.feedback else "N/A",
            "feedback": sub.feedback.overall_comment if sub.feedback else ""
        })
    
    # GPT-4로 오답 패턴 분석
    pattern_analysis = analyze_wrong_patterns_with_gpt(wrong_answers, subject)
    
    return {
        "analyzed_count": len(wrong_answers),
        "common_mistakes": pattern_analysis.get("common_mistakes", []),
        "misconceptions": pattern_analysis.get("misconceptions", []),
        "improvement_strategies": pattern_analysis.get("improvement_strategies", [])
    }


def generate_teaching_advice(
    db: Session,
    teacher_username: str,
    topic: str,
    subject: str = "국어"
) -> Dict[str, Any]:
    """
    수업자료 조언 생성
    
    Args:
        db: 데이터베이스 세션
        teacher_username: 교사 사용자명
        topic: 수업 주제
        subject: 과목
    
    Returns:
        수업자료 조언
    """
    # Record.score 평균 사용 (임시)
    avg_score_res = db.query(func.avg(Record.score)).scalar()
    avg_score = avg_score_res if avg_score_res else 70.0
    
    # GPT-4로 조언 생성
    advice = generate_advice_with_gpt(
        topic=topic,
        subject=subject,
        avg_score=float(avg_score)
    )
    
    return {
        "topic": topic,
        "subject": subject,
        "class_average": round(avg_score, 2),
        "lesson_objectives": advice.get("lesson_objectives", []),
        "teaching_methods": advice.get("teaching_methods", []),
        "materials": advice.get("materials", []),
        "assessment_tips": advice.get("assessment_tips", [])
    }


def analyze_questions_with_gpt(questions: List[str], subject: str) -> Dict[str, Any]:
    """GPT-4를 사용한 질문 분석"""
    if not questions:
        return {}
        
    questions_text = "\n".join([f"- {q}" for q in questions[:30]])  # 최대 30개
    
    prompt = f"""
    당신은 {subject} 교사입니다. 학생들이 최근에 한 질문들을 분석해주세요.
    
    **학생 질문 목록**:
    {questions_text}
    
    다음 형식의 JSON으로 분석 결과를 작성해주세요:
    {{
      "summary": "전체 질문 요약 (2-3문장)",
      "common_topics": ["자주 나온 주제1", "주제2", "주제3"],
      "difficulty_areas": ["학생들이 어려워하는 영역1", "영역2"],
      "teaching_suggestions": ["교수 제안사항1", "제안사항2", "제안사항3"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 데이터 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"질문 분석 중 오류: {e}")
        return {}


def analyze_wrong_patterns_with_gpt(wrong_answers: List[Dict], subject: str) -> Dict[str, Any]:
    """GPT-4를 사용한 오답 패턴 분석"""
    if not wrong_answers:
        return {}

    # 샘플 데이터만 전송 (토큰 제한)
    sample_data = wrong_answers[:10]
    answers_text = "\n\n".join([
        f"질문: {a['question'][:100]}\n학생답안: {a['student_answer'][:200]}\n평가: {a['score']}"
        for a in sample_data
    ])
    
    prompt = f"""
    당신은 {subject} 교사입니다. 학생들의 오답을 분석하여 공통 패턴을 찾아주세요.
    
    **오답 샘플**:
    {answers_text}
    
    다음 형식의 JSON으로 분석 결과를 작성해주세요:
    {{
      "common_mistakes": ["흔한 실수1", "실수2"],
      "misconceptions": ["오개념1", "오개념2"],
      "improvement_strategies": ["개선 전략1", "전략2"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 학습 평가 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"오답 패턴 분석 중 오류: {e}")
        return {}


def generate_advice_with_gpt(topic: str, subject: str, avg_score: float) -> Dict[str, Any]:
    """GPT-4를 사용한 수업자료 조언 생성"""
    prompt = f"""
    당신은 {subject} 교사입니다. 다음 주제에 대한 수업을 준비하고 있습니다.
    
    **수업 주제**: {topic}
    **학급 평균 점수**: {avg_score}점
    
    효과적인 수업을 위한 조언을 다음 형식의 JSON으로 작성해주세요:
    {{
      "lesson_objectives": ["학습 목표1", "목표2"],
      "teaching_methods": ["교수 방법1", "방법2"],
      "materials": ["필요한 자료1", "자료2"],
      "assessment_tips": ["평가 팁1", "팁2"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육과정 설계 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"수업자료 조언 생성 중 오류: {e}")
        return {}
