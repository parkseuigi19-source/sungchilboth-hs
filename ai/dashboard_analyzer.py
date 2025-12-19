"""
AI 성취 진단 대시보드 데이터 생성 모듈
학생별 단원별 성취도 분석 및 강약점 히트맵 생성
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import AchievementRecord, Record
import json
from datetime import datetime, timedelta


def analyze_student_achievement(db: Session, username: str, subject: str = "국어") -> Dict[str, Any]:
    """
    학생의 성취도를 분석하여 대시보드 데이터 생성
    """
    # 최근 30일 학습 기록 조회
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # 성취기준별 점수 집계 (AchievementRecord)
    achievement_stats = db.query(
        AchievementRecord.standard_code,
        func.avg(AchievementRecord.score).label('avg_score'),
        func.count(AchievementRecord.id).label('attempt_count')
    ).filter(
        and_(
            AchievementRecord.username == username,
            AchievementRecord.subject == subject,
            AchievementRecord.created_at >= thirty_days_ago
        )
    ).group_by(AchievementRecord.standard_code).all()
    
    # 학습 기록 조회 (Record 사용 - student_name 대신 username)
    learning_stats = db.query(
        func.avg(Record.score).label('avg_score'),
        func.count(Record.id).label('total_questions')
    ).filter(
        and_(
            Record.username == username,
            Record.created_at >= thirty_days_ago
        )
    ).first()
    
    # learning_stats가 None인 경우를 위한 안전한 기본값 설정
    avg_score_val = 0
    total_questions_val = 0
    if learning_stats:
        avg_score_val = round(learning_stats.avg_score or 0, 2)
        total_questions_val = learning_stats.total_questions or 0

    # 성취기준별 데이터 정리
    achievement_by_standard = {}
    for stat in achievement_stats:
        achievement_by_standard[stat.standard_code] = {
            "average_score": round(stat.avg_score, 2),
            "attempt_count": stat.attempt_count,
            "status": get_achievement_status(stat.avg_score)
        }
    
    # 강점/약점 분석 - 리스트만 유지
    strong_areas = []
    weak_areas = []
    
    for code, data in achievement_by_standard.items():
        if data["average_score"] >= 80:
            strong_areas.append({
                "standard_code": code,
                "score": data["average_score"]
            })
        elif data["average_score"] < 60:
            weak_areas.append({
                "standard_code": code,
                "score": data["average_score"]
            })
    
    return {
        "username": username,
        "subject": subject,
        "overall_stats": {
            "average_score": avg_score_val,
            "total_questions": total_questions_val,
            "analysis_period": "최근 30일"
        },
        "achievement_by_standard": achievement_by_standard,
        "strong_areas": sorted(strong_areas, key=lambda x: x["score"], reverse=True),
        "weak_areas": sorted(weak_areas, key=lambda x: x["score"]),
        "last_updated": datetime.now().isoformat()
    }


def generate_heatmap_data(db: Session, username: str, subject: str = "국어") -> Dict[str, Any]:
    """
    강약점 히트맵 데이터 생성
    """
    # 성취기준 목록 (실제로는 standards_engine에서 가져와야 함)
    standard_codes = ["K-HS-1", "K-HS-2", "K-HS-3", "K-HS-4", "K-HS-5", "K-HS-6", "K-HS-7"]
    
    # 각 성취기준별 최근 점수 조회
    heatmap_data = []
    
    for code in standard_codes:
        recent_scores = db.query(AchievementRecord.score).filter(
            and_(
                AchievementRecord.username == username,
                AchievementRecord.standard_code == code,
                AchievementRecord.subject == subject
            )
        ).order_by(AchievementRecord.created_at.desc()).limit(10).all()
        
        if recent_scores:
            scores = [s.score for s in recent_scores]
            avg_score = sum(scores) / len(scores)
            heatmap_data.append({
                "standard_code": code,
                "score": round(avg_score, 2),
                "intensity": get_heatmap_intensity(avg_score),
                "recent_attempts": len(scores)
            })
        else:
            heatmap_data.append({
                "standard_code": code,
                "score": 0,
                "intensity": 0,
                "recent_attempts": 0
            })
    
    return {
        "username": username,
        "subject": subject,
        "heatmap": heatmap_data,
        "legend": {
            "high": "80-100점 (강점)",
            "medium": "60-79점 (보통)",
            "low": "0-59점 (약점)"
        }
    }


def get_achievement_status(score: float) -> str:
    """점수에 따른 성취 상태 반환"""
    if score >= 80:
        return "우수"
    elif score >= 60:
        return "보통"
    else:
        return "미흡"


def get_heatmap_intensity(score: float) -> int:
    """히트맵 강도 계산 (0-10)"""
    return min(10, max(0, int(score / 10)))
