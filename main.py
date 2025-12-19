import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# ==================== 환경 변수 로드 ====================
load_dotenv()

# ==================== DB 초기화 ====================
from database import engine
from models import Base

# (개발 환경에서만)
Base.metadata.create_all(bind=engine)

# ==================== 라우터 임포트 ====================
from api.auth import router as auth_router

from api.analyzer_api import router as analyzer_router
from api.teacher_api import router as teacher_router
from api.report_api import router as report_router
from api.student_api import router as student_router
from api.agent_api import router as agent_router  # ✅ LangChain Agent (GPT-4o)

# 확장 기능 라우터
from api.dashboard_api import router as dashboard_router
from api.portfolio_api import router as portfolio_router
from api.grading_api import router as grading_router


# ==================== FastAPI 앱 생성 ====================
app = FastAPI(
    title="성취봇-HS",
    description="2022 개정 교육과정 반영 학습 지원 시스템",
    version="1.0.0"
)

# ==================== CORS 설정 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ 운영 시 특정 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 정적 파일 & 템플릿 설정 ====================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==================== 페이지 라우트 ====================
@app.get("/", tags=["Pages"])
def root():
    """메인 페이지 - 로그인으로 리디렉션"""
    return RedirectResponse(url="/login")

@app.get("/login", tags=["Pages"])
def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", tags=["Pages"])
def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/student", tags=["Pages"])
def student_page(request: Request):
    """학생용 채팅 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/student/dashboard", tags=["Pages"])
def student_dashboard(request: Request):
    """학생용 성취도 대시보드"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/student/grading", tags=["Pages"])
def student_grading(request: Request):
    """학생용 답안 제출 및 채점"""
    return templates.TemplateResponse("grading.html", {"request": request})

@app.get("/student/portfolio", tags=["Pages"])
def student_portfolio(request: Request):
    """학생용 E-포트폴리오"""
    return templates.TemplateResponse("portfolio.html", {"request": request})

@app.get("/teacher", tags=["Pages"])
def teacher_page(request: Request):
    """교사용 메인 - 대시보드로 리디렉션"""
    return RedirectResponse(url="/teacher/dashboard")

@app.get("/teacher/dashboard", tags=["Pages"])
def teacher_dashboard(request: Request):
    """교사용 대시보드"""
    return templates.TemplateResponse("teacher-dashboard.html", {"request": request})

@app.get("/teacher/class-report", tags=["Pages"])
def teacher_class_report(request: Request):
    """교사용 학급 리포트"""
    return templates.TemplateResponse("class-report.html", {"request": request})

@app.get("/teacher/batch-grading", tags=["Pages"])
def teacher_batch_grading(request: Request):
    """교사용 일괄 채점"""
    return templates.TemplateResponse("batch-grading.html", {"request": request})




# ==================== API 라우터 등록 ====================

# 👤 인증 / 계정
app.include_router(auth_router)

# 💬 일반 채팅 / 대화


# 🧠 LangChain Agent (GPT-4o 기반 교육용 챗봇)
app.include_router(agent_router)

# 📊 학습 분석 / 성취도
app.include_router(analyzer_router)

# 🎓 학생 관련 기능
app.include_router(student_router)

# 👩‍🏫 교사 관련 기능
app.include_router(teacher_router)

# 📑 리포트 / 보고서
app.include_router(report_router)

# ✨ 확장 기능 - 학생용
app.include_router(dashboard_router)  # 성취도 대시보드
app.include_router(portfolio_router)  # E-포트폴리오
app.include_router(grading_router)    # 채점 및 이력


# ==================== 헬스체크 ====================
@app.get("/health", tags=["System"])
def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "message": "Server is running"}


# ==================== 서버 실행 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 개발환경만
    )
