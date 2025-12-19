from database import SessionLocal
from ai.portfolio_generator import generate_portfolio_pdf, generate_portfolio_data
import os

def test_pdf_generation():
    db = SessionLocal()
    username = "testuser"
    
    print(f"Generating data for {username}...")
    generate_portfolio_data(db, username)
    
    print(f"Generating PDF for {username}...")
    pdf_path = generate_portfolio_pdf(db, username)
    
    print(f"PDF generated at: {pdf_path}")
    
    full_path = f"c:/AIX/sungchibot-hs{pdf_path}"
    if os.path.exists(full_path):
        print("Success: PDF file exists.")
    else:
        print(f"Error: PDF file not found at {full_path}")
    
    db.close()

if __name__ == "__main__":
    test_pdf_generation()
