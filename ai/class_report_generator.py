"""
학급 성취도 리포트 자동 생성
단원별 성취도 차트 및 리딩 포인트 생성
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import ClassReport, Record
from openai import OpenAI
from config import settings
from datetime import datetime
import json
import os
from utils.pdf_utils import create_class_report_pdf


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_class_report(
    db: Session,
    teacher_username: str,
    class_name: str,
    subject: str = "국어",
    report_type: str = "unit",
    student_list: List[str] = None
) -> Dict[str, Any]:
    """
    학급 성취도 리포트 생성
    """
    # 학생 목록이 없으면 전체 학생 조회 (Record 기반)
    if not student_list:
        student_list = get_all_students(db, subject)
    
    # 학급 전체 통계
    total_students = len(student_list)
    
    # 학생별 평균 점수 계산
    student_scores = []
    for student in student_list:
        # Record 테이블의 score 사용
        avg_score = db.query(func.avg(Record.score)).filter(
            and_(
                Record.username == student,
                # Record에는 명시적 subject가 없으므로 생략하거나 추후 보완
                # 여기서는 모든 과목 평균으로 가정
            )
        ).scalar()
        
        if avg_score:
            student_scores.append({
                "username": student,
                "average_score": round(avg_score, 2)
            })
    
    # 학급 평균
    class_average = sum(s["average_score"] for s in student_scores) / len(student_scores) if student_scores else 0
    
    # 상위/하위 학생
    sorted_students = sorted(student_scores, key=lambda x: x["average_score"], reverse=True)
    top_achievers = sorted_students[:3] if len(sorted_students) >= 3 else sorted_students
    struggling_students = sorted_students[-3:] if len(sorted_students) >= 3 else []
    
    # 단원별 성취도 분석 (임시: Record category 사용)
    unit_analysis = analyze_unit_achievement(db, student_list, subject)
    
    # GPT-4로 리딩 포인트 생성
    leading_points = generate_leading_points_with_gpt(
        class_average=class_average,
        unit_analysis=unit_analysis,
        struggling_count=len(struggling_students)
    )
    
    # 데이터베이스에 저장
    new_report = ClassReport(
        teacher_username=teacher_username,
        class_name=class_name,
        subject=subject,
        report_type=report_type,
        total_students=total_students,
        average_score=round(class_average, 2),
        top_achievers=json.dumps(top_achievers, ensure_ascii=False),
        struggling_students=json.dumps(struggling_students, ensure_ascii=False),
        unit_analysis=json.dumps(unit_analysis, ensure_ascii=False),
        leading_points=leading_points
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # PDF 생성
    try:
        os.makedirs("static/reports", exist_ok=True)
        filename = f"class_report_{new_report.id}.pdf"
        pdf_path = f"/static/reports/{filename}"
        full_pdf_path = os.path.join("static/reports", filename)
        
        # 리포트 데이터 구성을 API 반환 형식과 맞춤
        report_data = {
            "class_name": class_name,
            "subject": subject,
            "total_students": total_students,
            "average_score": round(class_average, 2),
            "leading_points": leading_points,
            "student_scores": student_scores, # 학생별 평균 점수 리스트
            "unit_analysis": unit_analysis   # 단원별 성취도 분석
        }
        
        create_class_report_pdf(report_data, full_pdf_path)
        
        # DB 업데이트
        new_report.pdf_path = pdf_path
        db.commit()
    except Exception as e:
        print(f"PDF 생성 중 오류 발생: {e}")
    
    return {
        "report_id": new_report.id,
        "class_name": class_name,
        "subject": subject,
        "report_type": report_type,
        "total_students": total_students,
        "average_score": round(class_average, 2),
        "top_achievers": top_achievers,
        "struggling_students": struggling_students,
        "unit_analysis": unit_analysis,
        "leading_points": leading_points,
        "generated_at": new_report.created_at.isoformat()
    }


def analyze_unit_achievement(
    db: Session,
    student_list: List[str],
    subject: str
) -> List[Dict[str, Any]]:
    """
    단원별 성취도 분석 (Record category 기반 Mocking)
    """
    # Record의 category를 단원 코드로 가정
    unit_data = []
    
    # 임시 단원 코드 목록
    standard_codes = ["K-HS-1", "K-HS-2", "K-HS-3"]
    
    for code in standard_codes:
        # 실제 데이터가 충분하지 않을 수 있으므로 Mocking 로직 포함
        scores = db.query(Record.score).filter(
            and_(
                Record.username.in_(student_list),
                Record.category.like(f"%{code}%")
            )
        ).all()
        
        if scores:
            score_values = [s.score for s in scores]
            avg_score = sum(score_values) / len(score_values)
            unit_data.append({
                "standard_code": code,
                "average_score": round(avg_score, 2),
                "student_count": len(set(score_values)),
                "status": "우수" if avg_score >= 80 else "보통"
            })
        else:
             unit_data.append({
                "standard_code": code,
                "average_score": 0,
                "student_count": 0,
                "status": "데이터 없음"
            })
    
    return unit_data


def generate_leading_points_with_gpt(
    class_average: float,
    unit_analysis: List[Dict],
    struggling_count: int
) -> str:
    """GPT-4 생성"""
    unit_summary = "\n".join([
        f"- {u['standard_code']}: {u['average_score']}점 ({u['status']})"
        for u in unit_analysis
    ])
    
    prompt = f"""
    당신은 고등학교 국어 교사입니다. 학급 성취도 리포트를 작성하고 있습니다.
    
    **학급 평균**: {class_average}점
    **학습 부진 학생 수**: {struggling_count}명
    
    **단원별 성취도**:
    {unit_summary}
    
    이 데이터를 바탕으로 교사가 주목해야 할 **주요 지도 포인트**를 3-5개 작성해주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 평가 및 지도 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return "리딩 포인트를 생성할 수 없습니다."


def get_all_students(db: Session, subject: str) -> List[str]:
    """과목별 전체 학생 목록 조회"""
    students = db.query(Record.username).distinct().all()
    return [s.username for s in students if s.username]


def get_class_report(db: Session, report_id: int) -> Dict[str, Any]:
    """저장된 학급 리포트 조회"""
    report = db.query(ClassReport).filter(ClassReport.id == report_id).first()
    
    if not report:
        return None
    
    return {
        "report_id": report.id,
        "teacher_username": report.teacher_username,
        "class_name": report.class_name,
        "subject": report.subject,
        "report_type": report.report_type,
        "total_students": report.total_students,
        "average_score": report.average_score,
        "top_achievers": json.loads(report.top_achievers) if report.top_achievers else [],
        "struggling_students": json.loads(report.struggling_students) if report.struggling_students else [],
        "unit_analysis": json.loads(report.unit_analysis) if report.unit_analysis else [],
        "leading_points": report.leading_points,
        "pdf_path": report.pdf_path,
        "created_at": report.created_at.isoformat()
    }
