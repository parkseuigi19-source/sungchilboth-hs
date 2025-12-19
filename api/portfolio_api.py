"""
포트폴리오 API
E-포트폴리오 생성 및 PDF 다운로드
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import engine
from models import Base
from ai.portfolio_generator import generate_portfolio_data, get_portfolio, generate_portfolio_pdf
from pydantic import BaseModel
import os


router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


class PortfolioRequest(BaseModel):
    username: str
    subject: str = "국어"


@router.post("/data")
def get_portfolio_data(request: PortfolioRequest, db: Session = Depends(get_db)):
    """
    포트폴리오 데이터 조회 (없으면 생성)
    """
    try:
        print(f"DEBUG: [Portfolio] Request received for user: {request.username}")
        
        # 기존 포트폴리오 조회
        portfolio = get_portfolio(db=db, username=request.username)
        print(f"DEBUG: [Portfolio] Existing portfolio found: {bool(portfolio)}")
        
        if not portfolio:
            # 없으면 생성
            print(f"DEBUG: [Portfolio] Generating new data for {request.username}...")
            portfolio = generate_portfolio_data(
                db=db,
                username=request.username,
                subject=request.subject
            )
            print("DEBUG: [Portfolio] Generation complete.")
        
        print("DEBUG: [Portfolio] Returning response.")
        return {"success": True, "data": portfolio}
    except Exception as e:
        print(f"ERROR: [Portfolio] Failed to get/generate data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"포트폴리오 조회 실패: {str(e)}")


@router.post("/generate-pdf")
def generate_pdf(request: PortfolioRequest, db: Session = Depends(get_db)):
    """
    포트폴리오 PDF 생성
    
    Args:
        request: 요청 데이터
        db: 데이터베이스 세션
    
    Returns:
        PDF 파일 경로
    """
    try:
        pdf_path = generate_portfolio_pdf(
            db=db,
            username=request.username
        )
        
        return {
            "success": True,
            "message": "PDF가 생성되었습니다.",
            "pdf_path": pdf_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 실패: {str(e)}")


@router.get("/download/{username}")
def download_pdf(username: str, db: Session = Depends(get_db)):
    """
    포트폴리오 PDF 다운로드
    
    Args:
        username: 학생 사용자명
        db: 데이터베이스 세션
    
    Returns:
        PDF 파일
    """
    try:
        portfolio = get_portfolio(db=db, username=username)
        
        if not portfolio or not portfolio.get("pdf_path"):
            raise HTTPException(status_code=404, detail="PDF 파일을 찾을 수 없습니다.")
        
        pdf_path = portfolio["pdf_path"]
        
        # static으로 시작하면 루트 경로 결합
        if pdf_path.startswith("/"):
            pdf_path_rel = pdf_path[1:]
        else:
            pdf_path_rel = pdf_path
            
        abs_path = os.path.join(os.getcwd(), pdf_path_rel.replace("/", os.sep))
        
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail=f"PDF 파일이 존재하지 않습니다: {abs_path}")
        
        return FileResponse(
            path=abs_path,
            filename=f"portfolio_{username}.pdf",
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 다운로드 실패: {str(e)}")
