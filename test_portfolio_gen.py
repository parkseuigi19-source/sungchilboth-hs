from database import SessionLocal
from ai.portfolio_generator import generate_portfolio_data, generate_portfolio_pdf
import os

def test_portfolio_gen():
    db = SessionLocal()
    # 테스트용 사용자 (DB에 존재해야 함, 없을 경우 생성 로직 필요하지만 일단 가정)
    username = "testuser" 
    
    print(f"'{username}' 사용자에 대한 포트폴리오 생성 테스트 중...")
    
    # 1. 데이터 생성 테스트
    try:
        data = generate_portfolio_data(db, username)
        print("데이터 생성 성공:", data.keys())
    except Exception as e:
        print(f"데이터 생성 실패: {e}")
        db.close()
        return

    # 2. PDF 생성 테스트
    try:
        pdf_path = generate_portfolio_pdf(db, username)
        print(f"PDF 생성 경로: {pdf_path}")
        
        # 실제 파일 존재 확인
        # web_path가 '/static/...' 으로 반환됨.
        abs_path = os.path.join(os.getcwd(), pdf_path.lstrip('/'))
        if os.path.exists(abs_path):
            print("성공: PDF 파일이 존재합니다.")
        else:
            print(f"오류: PDF 파일을 찾을 수 없습니다: {abs_path}")
            
    except Exception as e:
        print(f"PDF 생성 실패: {e}")
    
    db.close()

if __name__ == "__main__":
    test_portfolio_gen()
