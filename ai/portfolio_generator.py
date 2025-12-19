"""
E-포트폴리오 생성 모듈
학생의 학습 기록을 수집하여 PDF 포트폴리오 생성
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Portfolio, Record, AchievementRecord, EssayGrading
from datetime import datetime
import json
import os


def generate_portfolio_data(db: Session, username: str, subject: str = "국어") -> Dict[str, Any]:
    """
    포트폴리오 데이터 생성
    """
    # 학습 기록 통계 (Record 사용)
    learning_stats = db.query(
        func.count(Record.id).label('total_questions'),
        func.avg(Record.score).label('avg_score'),
        func.sum(Record.score).label('total_score')
    ).filter(
        and_(
            Record.username == username,
            # Record does not have explicit subject in my current schema, 
            # assuming handled or we take all records for now.
        )
    ).first()
    
    # 성취기준별 점수
    achievement_by_standard = db.query(
        AchievementRecord.standard_code,
        func.avg(AchievementRecord.score).label('avg_score'),
        func.count(AchievementRecord.id).label('count')
    ).filter(
        and_(
            AchievementRecord.username == username,
            AchievementRecord.subject == subject
        )
    ).group_by(AchievementRecord.standard_code).all()
    
    # 강점/약점 영역 분석
    strong_areas = []
    weak_areas = []
    
    for achievement in achievement_by_standard:
        area_data = {
            "standard_code": achievement.standard_code,
            "average_score": round(achievement.avg_score, 2),
            "attempt_count": achievement.count
        }
        
        if achievement.avg_score >= 80:
            strong_areas.append(area_data)
        elif achievement.avg_score < 60:
            weak_areas.append(area_data)
    
    # 최근 서술형 채점 결과
    recent_essays = db.query(EssayGrading).filter(
        and_(
            EssayGrading.username == username,
            EssayGrading.subject == subject
        )
    ).order_by(EssayGrading.created_at.desc()).limit(5).all()
    
    essay_history = [
        {
            "question": e.question[:50] + "...",
            "score": e.score,
            "date": e.created_at.strftime("%Y-%m-%d")
        }
        for e in recent_essays
    ]
    
    # 주요 학습 기록 (상세 테이블용)
    recent_records = db.query(Record).filter(
        Record.username == username
    ).order_by(Record.created_at.desc()).limit(10).all()
    
    learning_history = [
        {
            "date": r.created_at.strftime("%Y-%m-%d"),
            "subject": r.category if r.category else "국어",
            "topic": r.question[:30] if r.question else "일반 학습",
            "score": r.score
        }
        for r in recent_records
    ]
    
    # 성취도 추이 데이터 (최근 5회분)
    progress_records = db.query(Record).filter(
        Record.username == username
    ).order_by(Record.created_at.asc()).all()
    
    if len(progress_records) > 5:
        progress_records = progress_records[-5:]
        
    trend_data = [
        {"label": f"{i+1}주", "score": r.score} 
        for i, r in enumerate(progress_records)
    ]
    
    # 영역별 성취도 (레이더 차트용)
    area_scores = {}
    for achievement in achievement_by_standard:
        # standard_code에서 영역 추출 (예: '문법', '문학', '독서')
        # 실제 데이터에 따라 파싱 로직 필요, 여기서는 예시로 매핑
        area_name = achievement.standard_code # 또는 매핑 테이블 사용
        area_scores[area_name] = round(achievement.avg_score, 2)
    
    # 포트폴리오 데이터 구성
    portfolio_data = {
        "username": username,
        "subject": subject,
        "total_questions": int(learning_stats.total_questions or 0),
        "total_score": round(float(learning_stats.total_score or 0), 2),
        "average_score": round(float(learning_stats.avg_score or 0), 2),
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "trend_data": trend_data,
        "area_scores": area_scores,
        "learning_history": learning_history,
        "generated_at": datetime.now().isoformat()
    }
    
    # 데이터베이스에 저장/업데이트
    existing_portfolio = db.query(Portfolio).filter(
        Portfolio.username == username
    ).first()
    
    if existing_portfolio:
        existing_portfolio.subject = subject
        existing_portfolio.total_questions = portfolio_data["total_questions"]
        existing_portfolio.total_score = portfolio_data["total_score"]
        existing_portfolio.average_score = portfolio_data["average_score"]
        existing_portfolio.strong_areas = json.dumps(strong_areas, ensure_ascii=False)
        existing_portfolio.weak_areas = json.dumps(weak_areas, ensure_ascii=False)
        existing_portfolio.learning_progress = json.dumps(trend_data, ensure_ascii=False)
        existing_portfolio.updated_at = datetime.now()
    else:
        new_portfolio = Portfolio(
            username=username,
            subject=subject,
            total_questions=portfolio_data["total_questions"],
            total_score=portfolio_data["total_score"],
            average_score=portfolio_data["average_score"],
            strong_areas=json.dumps(strong_areas, ensure_ascii=False),
            weak_areas=json.dumps(weak_areas, ensure_ascii=False),
            learning_progress=json.dumps(trend_data, ensure_ascii=False)
        )
        db.add(new_portfolio)
    
    db.commit()
    
    return portfolio_data


def get_portfolio(db: Session, username: str) -> Dict[str, Any]:
    """저장된 포트폴리오 데이터 조회"""
    portfolio = db.query(Portfolio).filter(Portfolio.username == username).first()
    
    if not portfolio:
        return None
    
    return {
        "username": portfolio.username,
        "subject": portfolio.subject,
        "total_questions": portfolio.total_questions,
        "total_score": portfolio.total_score,
        "average_score": portfolio.average_score,
        "strong_areas": json.loads(portfolio.strong_areas) if portfolio.strong_areas else [],
        "weak_areas": json.loads(portfolio.weak_areas) if portfolio.weak_areas else [],
        "learning_progress": json.loads(portfolio.learning_progress) if portfolio.learning_progress else [],
        "pdf_path": portfolio.pdf_path,
        "last_updated": portfolio.updated_at.isoformat() if portfolio.updated_at else portfolio.created_at.isoformat()
    }


def generate_portfolio_pdf(db: Session, username: str, output_dir: str = "static/portfolios") -> str:
    """포트폴리오 PDF 생성"""
    portfolio_data = get_portfolio(db, username)
    if not portfolio_data:
        portfolio_data = generate_portfolio_data(db, username)
    
    # 절대 경로 확보
    base_dir = os.getcwd()
    abs_output_dir = os.path.join(base_dir, output_dir.replace("/", os.sep))
    os.makedirs(abs_output_dir, exist_ok=True)
    
    pdf_filename = f"portfolio_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    # 실제 파일 시스템 저장 경로 (절대 경로)
    full_path = os.path.join(abs_output_dir, pdf_filename)
    # 웹 접근 가능한 상대 경로
    web_path = f"/{output_dir.strip('/')}/{pdf_filename}"
    
    # Try import pdf utils, if fail, skip
    try:
        from utils.pdf_utils import create_portfolio_pdf
        create_portfolio_pdf(portfolio_data, full_path)
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        # Create dummy file if utils missing or failed
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"PDF Generation failed: {str(e)}")
    
    portfolio = db.query(Portfolio).filter(Portfolio.username == username).first()
    if portfolio:
        # DB에는 웹 접근이 가능한 상대 경로를 저장
        portfolio.pdf_path = web_path
        db.commit()
    
    return web_path
