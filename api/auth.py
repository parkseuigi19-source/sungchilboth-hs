# api/auth.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User

# ✅ prefix 추가
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _read_body(request: Request):
    """JSON 또는 Form 데이터 타입 확인"""
    ct = request.headers.get("content-type", "")
    return "json" in ct


@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트
    - 실제 경로: /api/auth/register
    """
    try:
        if _read_body(request):
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form)
    except Exception as e:
        return {"success": False, "message": f"입력 파싱 오류: {e}"}

    try:
        # 입력 데이터 타입 안전 처리
        username = str(data.get("username") or "").strip()
        password = str(data.get("password") or "").strip()
        role = str(data.get("role") or "student").strip()

        if not username or not password:
            return {"success": False, "message": "아이디와 비밀번호는 필수입니다."}

        # 중복 체크
        exists = db.query(User).filter(User.username == username).first()
        if exists:
            return {"success": False, "message": "이미 존재하는 아이디입니다."}

        # 새 사용자 생성
        user = User(username=username, password_hash=password, name=username, role=role)
        db.add(user)
        db.commit()
        
        return {
            "success": True,
            "message": "회원가입 완료",
            "role": role
        }
    except Exception as e:
        print(f"회원가입 중 오류 발생: {e}")
        return {"success": False, "message": "회원가입 처리 중 서버 오류가 발생했습니다."}


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """
    로그인 엔드포인트
    - 실제 경로: /api/auth/login
    """
    try:
        if _read_body(request):
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form)
    except Exception as e:
        return {"success": False, "message": f"입력 파싱 오류: {e}"}

    try:
        # 입력 데이터 타입 안전 처리
        username = str(data.get("username") or "").strip()
        password = str(data.get("password") or "").strip()

        if not username or not password:
            return {"success": False, "message": "아이디와 비밀번호는 필수입니다."}

        # 사용자 인증
        user = db.query(User).filter(
            User.username == username,
            User.password_hash == password
        ).first()

        if not user:
            return {
                "success": False,
                "message": "아이디 또는 비밀번호가 올바르지 않습니다."
            }

        return {
            "success": True,
            "username": user.username,
            "role": user.role
        }
    except Exception as e:
        print(f"로그인 중 오류 발생: {e}")
        # 구체적인 오류 내용은 보안상 로그에만 남기고 사용자에게는 일반 메시지 전달
        return {"success": False, "message": "로그인 처리 중 서버 오류가 발생했습니다."}
