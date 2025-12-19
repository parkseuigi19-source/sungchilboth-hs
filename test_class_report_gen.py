from ai.class_report_generator import generate_class_report
from database import SessionLocal
import os

def test_class_report_gen():
    db = SessionLocal()
    teacher_username = "teacher1" # 가정
    class_name = "테스트반"
    student_list = ["student1", "student2"] # 가정 (DB에 있어야 함, 없으면 에러 날 수도)
    
    print("학급 리포트 생성 테스트 중...")
    try:
        result = generate_class_report(
            db=db,
            teacher_username=teacher_username,
            class_name=class_name,
            student_list=student_list
        )
        print("리포트 생성 결과:", result.keys())
        
        # PDF 경로 확인
        # generate_class_report는 result에 pdf_path를 포함하지 않고 get_class_report를 따로 해야 하거나
        # 반환값에 포함되어 있는지 확인 (코드상으로는 포함됨)
        # get_class_report 함수 내용이 result에 포함되어있는지 확인해보니, 
        # generate_class_report의 return dict에는 'generated_at' 등은 있지만 'pdf_path'는 명시적으로 반환 딕셔너리에 없음.
        # 하지만 DB에는 저장됨.
        
        from models import ClassReport
        report = db.query(ClassReport).filter(ClassReport.id == result['report_id']).first()
        if report and report.pdf_path:
            print(f"PDF 생성 성공: {report.pdf_path}")
            abs_path = os.path.join(os.getcwd(), report.pdf_path.lstrip('/'))
            if os.path.exists(abs_path):
                 print("파일 존재 확인됨.")
            else:
                 print(f"파일 없음: {abs_path}")
        else:
            print("PDF 생성 실패: DB에 경로가 없습니다.")

    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_class_report_gen()
