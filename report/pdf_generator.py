from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def make_student_report(pdf_path: str, username: str, records: list):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    W, H = A4
    y = H - 25*mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, y, f"성취도 리포트 - {username}")
    y -= 12*mm
    c.setFont("Helvetica", 11)

    for r in records:
        line = f"[{r['created_at'][:10]}] {r['category']} | {r['score']}점 | 수준 {r['level']} | 코드 {r['standard_code']}"
        c.drawString(20*mm, y, line)
        y -= 8*mm
        c.drawString(25*mm, y, f"피드백: {r['feedback']}")
        y -= 10*mm
        if y < 30*mm:
            c.showPage()
            y = H - 25*mm

    c.save()
    return pdf_path
