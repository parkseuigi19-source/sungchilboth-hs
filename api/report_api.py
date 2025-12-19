# api/report_api.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

router = APIRouter()

def _has_table_and_cols(db: Session, table: str, cols: list[str]) -> bool:
    # sqlite 전용: PRAGMA로 컬럼 조사
    try:
        rows = db.execute(text(f"PRAGMA table_info({table})")).fetchall()
        have = {r[1] for r in rows}  # 0:cid, 1:name, 2:type ...
        return all(c in have for c in cols)
    except Exception:
        return False

@router.get("/report/summary")
def report_summary(
    username: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    학생 성취 요약(테이블/컬럼 자동 감지):
    - percent: 평균 점수(정수, 0~100)
    - feedback: 최근 3건 피드백
    """
    percent = 0
    feedback: list[str] = []

    try:
        # 1) 최신 스키마: records(username, score, reply, category, created_at)
        if _has_table_and_cols(db, "records",
                               ["username", "score", "reply", "category", "created_at"]):
            avg_row = db.execute(text("""
                SELECT AVG(score) FROM records
                WHERE username=:u AND score IS NOT NULL AND score > 0
            """), {"u": username}).fetchone()
            percent = int(float(avg_row[0] or 0))

            fb_rows = db.execute(text("""
                SELECT reply FROM records
                WHERE username=:u AND category LIKE '서술형-%'
                ORDER BY datetime(created_at) DESC
                LIMIT 3
            """), {"u": username}).fetchall()
            feedback = [r[0] for r in fb_rows if r and r[0]]

        # 2) 예전 스키마: learning_records(student_name, score, feedback, created_at)
        elif _has_table_and_cols(db, "learning_records",
                                 ["student_name", "score", "feedback", "created_at"]):
            avg_row = db.execute(text("""
                SELECT AVG(score) FROM learning_records
                WHERE student_name=:u AND score IS NOT NULL AND score > 0
            """), {"u": username}).fetchone()
            percent = int(float(avg_row[0] or 0))

            fb_rows = db.execute(text("""
                SELECT feedback FROM learning_records
                WHERE student_name=:u
                ORDER BY datetime(created_at) DESC
                LIMIT 3
            """), {"u": username}).fetchall()
            feedback = [r[0] for r in fb_rows if r and r[0]]

        # 3) 어떤 것도 없으면 기본값
        else:
            percent, feedback = 0, []

    except Exception as e:
        # 실패해도 API 자체는 터지지 않도록
        print("[report_summary] error:", e)
        percent, feedback = 0, []

    return {"success": True, "username": username, "percent": percent, "feedback": feedback}
