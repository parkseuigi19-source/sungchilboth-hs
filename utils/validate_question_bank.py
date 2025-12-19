"""
문항 은행 일괄 검증 스크립트
기존에 저장된 문제들의 수준을 검증하고 리포트 생성
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import QuestionBank, ProblemValidation
from ai.level_validator import batch_validate_problems, get_validation_statistics
from datetime import datetime
import json
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_question_bank(
    db: Session,
    subject: str = "국어",
    target_grade: str = "고등학교",
    save_to_db: bool = True,
    output_file: str = None
):
    """
    문항 은행의 모든 문제를 검증합니다.
    
    Args:
        db: 데이터베이스 세션
        subject: 과목
        target_grade: 목표 학년
        save_to_db: 검증 결과를 DB에 저장할지 여부
        output_file: 결과를 저장할 파일 경로 (JSON)
    """
    logger.info(f"=== 문항 은행 검증 시작 ===")
    logger.info(f"과목: {subject}, 목표 학년: {target_grade}")
    
    # 문항 은행에서 모든 문제 조회
    questions = db.query(QuestionBank).filter(
        QuestionBank.subject == subject
    ).all()
    
    if not questions:
        logger.warning("검증할 문제가 없습니다.")
        return
    
    logger.info(f"총 {len(questions)}개 문제 검증 시작...")
    
    # 검증할 문제 리스트 구성
    problems_to_validate = []
    for q in questions:
        problems_to_validate.append({
            "id": q.id,
            "question": q.question_text,
            "difficulty": q.difficulty,
            "standard_code": q.standard_code
        })
    
    # 일괄 검증
    validation_results = batch_validate_problems(
        problems=problems_to_validate,
        target_grade=target_grade,
        subject=subject
    )
    
    # 통계 생성
    stats = get_validation_statistics(validation_results)
    
    logger.info(f"\n=== 검증 결과 통계 ===")
    logger.info(f"총 문제 수: {stats['total']}")
    logger.info(f"적절한 문제: {stats['appropriate']} ({stats['appropriate_rate']:.1f}%)")
    logger.info(f"부적절한 문제: {stats['inappropriate']}")
    logger.info(f"평균 신뢰도: {stats['average_confidence']:.1f}%")
    logger.info(f"\n수준별 분포:")
    for level, count in stats['level_distribution'].items():
        logger.info(f"  - {level}: {count}개")
    
    # 부적절한 문제 목록
    inappropriate_problems = [
        r for r in validation_results if not r.get("is_appropriate", False)
    ]
    
    if inappropriate_problems:
        logger.warning(f"\n=== 부적절한 문제 목록 ({len(inappropriate_problems)}개) ===")
        for idx, problem in enumerate(inappropriate_problems, 1):
            logger.warning(f"\n[{idx}] 문제 ID: {problems_to_validate[problem['problem_index']]['id']}")
            logger.warning(f"감지된 수준: {problem['detected_level']}")
            logger.warning(f"신뢰도: {problem['confidence']:.1f}%")
            logger.warning(f"이유: {problem['reason']}")
            logger.warning(f"문제: {problem['problem_text'][:100]}...")
    
    # 데이터베이스에 저장
    if save_to_db:
        logger.info("\n검증 결과를 데이터베이스에 저장 중...")
        saved_count = 0
        
        for result in validation_results:
            problem_idx = result['problem_index']
            original_problem = problems_to_validate[problem_idx]
            
            validation_record = ProblemValidation(
                problem_id=original_problem['id'],
                problem_source='question_bank',
                problem_text=result['problem_text'],
                target_grade=target_grade,
                detected_level=result['detected_level'],
                is_appropriate=1 if result['is_appropriate'] else 0,
                confidence_score=result['confidence'],
                validation_reason=result['reason'],
                suggestions=result.get('suggestions', ''),
                validated_at=datetime.now()
            )
            
            db.add(validation_record)
            saved_count += 1
        
        db.commit()
        logger.info(f"✓ {saved_count}개 검증 결과 저장 완료")
    
    # JSON 파일로 저장
    if output_file:
        report = {
            "validation_date": datetime.now().isoformat(),
            "subject": subject,
            "target_grade": target_grade,
            "statistics": stats,
            "results": validation_results
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 검증 리포트 저장: {output_file}")
    
    logger.info("\n=== 검증 완료 ===")
    
    return {
        "statistics": stats,
        "inappropriate_problems": inappropriate_problems,
        "validation_results": validation_results
    }


def main():
    """메인 실행 함수"""
    db = SessionLocal()
    
    try:
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"validation_report_{timestamp}.json"
        
        # 검증 실행
        result = validate_question_bank(
            db=db,
            subject="국어",
            target_grade="고등학교",
            save_to_db=True,
            output_file=output_file
        )
        
        # 요약 출력
        if result:
            stats = result['statistics']
            print(f"\n{'='*50}")
            print(f"검증 완료!")
            print(f"적절한 문제: {stats['appropriate']}/{stats['total']} ({stats['appropriate_rate']:.1f}%)")
            print(f"리포트 파일: {output_file}")
            print(f"{'='*50}\n")
        
    except Exception as e:
        logger.error(f"검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
