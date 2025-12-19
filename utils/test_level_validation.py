"""
문제 수준 검증 시스템 테스트
다양한 수준의 샘플 문제로 검증 정확도 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from ai.level_validator import validate_problem_level, get_validation_statistics
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 테스트 샘플 문제
TEST_PROBLEMS = {
    "초등학교_수준": [
        {
            "question": "사과는 무슨 색인가요?",
            "difficulty": "easy",
            "expected_level": "초등학교",
            "should_reject": True
        },
        {
            "question": "다음 중 동물이 아닌 것을 고르세요: 개, 고양이, 책상, 토끼",
            "difficulty": "easy",
            "expected_level": "초등학교",
            "should_reject": True
        }
    ],
    
    "중학교_수준": [
        {
            "question": "다음 문장에서 주어를 찾으시오: '철수가 학교에 갔다.'",
            "difficulty": "easy",
            "expected_level": "중학교",
            "should_reject": True
        },
        {
            "question": "비유법의 종류를 3가지 쓰시오.",
            "difficulty": "medium",
            "expected_level": "중학교",
            "should_reject": True
        }
    ],
    
    "고등학교_수준": [
        {
            "question": """다음 시를 읽고 물음에 답하시오.

'님은 갔습니다. 아아, 사랑하는 나의 님은 갔습니다.'

이 작품에서 화자의 태도 변화를 분석하고, 이것이 주제 전달에 미치는 영향을 서술하시오.""",
            "difficulty": "medium",
            "expected_level": "고등학교",
            "should_reject": False
        },
        {
            "question": """제시된 논설문을 읽고, 필자의 주장과 논거를 분석한 후, 반론을 제시하고 그 타당성을 논리적으로 설명하시오.""",
            "difficulty": "hard",
            "expected_level": "고등학교",
            "should_reject": False
        },
        {
            "question": """다음 소설의 서술 시점을 분석하고, 이러한 서술 방식이 독자의 작품 이해에 미치는 효과를 구체적으로 논하시오.""",
            "difficulty": "medium",
            "expected_level": "고등학교",
            "should_reject": False
        }
    ],
    
    "대학_수준": [
        {
            "question": "후기구조주의 관점에서 텍스트의 해체적 읽기를 시도하고, 데리다의 차연(différance) 개념을 적용하여 분석하시오.",
            "difficulty": "hard",
            "expected_level": "대학",
            "should_reject": True
        },
        {
            "question": "바흐친의 대화주의 이론을 바탕으로 소설 텍스트의 다성성(polyphony)을 분석하시오.",
            "difficulty": "hard",
            "expected_level": "대학",
            "should_reject": True
        }
    ]
}


def run_validation_tests():
    """검증 테스트 실행"""
    logger.info("="*60)
    logger.info("문제 수준 검증 시스템 테스트 시작")
    logger.info("="*60)
    
    all_results = []
    correct_predictions = 0
    total_tests = 0
    
    for level_category, problems in TEST_PROBLEMS.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"테스트 카테고리: {level_category}")
        logger.info(f"{'='*60}")
        
        for idx, problem in enumerate(problems, 1):
            total_tests += 1
            logger.info(f"\n[테스트 {total_tests}] {level_category} - 문제 {idx}")
            logger.info(f"문제: {problem['question'][:100]}...")
            logger.info(f"예상 수준: {problem['expected_level']}")
            logger.info(f"거부되어야 함: {problem['should_reject']}")
            
            # 검증 실행
            validation = validate_problem_level(
                question_text=problem['question'],
                target_grade="고등학교",
                subject="국어",
                difficulty=problem['difficulty']
            )
            
            # 결과 분석
            is_correct = (not validation['is_appropriate']) == problem['should_reject']
            
            if is_correct:
                correct_predictions += 1
                result_symbol = "✓"
            else:
                result_symbol = "✗"
            
            logger.info(f"\n{result_symbol} 검증 결과:")
            logger.info(f"  - 감지된 수준: {validation['detected_level']}")
            logger.info(f"  - 적절성: {'적절' if validation['is_appropriate'] else '부적절'}")
            logger.info(f"  - 신뢰도: {validation['confidence']:.1f}%")
            logger.info(f"  - 판단 근거: {validation['reason'][:150]}...")
            logger.info(f"  - 예측 정확도: {'정확' if is_correct else '부정확'}")
            
            all_results.append({
                "category": level_category,
                "problem": problem['question'][:100],
                "expected_level": problem['expected_level'],
                "detected_level": validation['detected_level'],
                "should_reject": problem['should_reject'],
                "is_appropriate": validation['is_appropriate'],
                "confidence": validation['confidence'],
                "is_correct": is_correct
            })
    
    # 전체 통계
    accuracy = (correct_predictions / total_tests * 100) if total_tests > 0 else 0
    
    logger.info(f"\n{'='*60}")
    logger.info("테스트 결과 요약")
    logger.info(f"{'='*60}")
    logger.info(f"총 테스트: {total_tests}개")
    logger.info(f"정확한 예측: {correct_predictions}개")
    logger.info(f"부정확한 예측: {total_tests - correct_predictions}개")
    logger.info(f"정확도: {accuracy:.1f}%")
    
    # 카테고리별 통계
    logger.info(f"\n카테고리별 결과:")
    for level_category in TEST_PROBLEMS.keys():
        category_results = [r for r in all_results if r['category'] == level_category]
        category_correct = sum(1 for r in category_results if r['is_correct'])
        category_total = len(category_results)
        category_accuracy = (category_correct / category_total * 100) if category_total > 0 else 0
        
        logger.info(f"  - {level_category}: {category_correct}/{category_total} ({category_accuracy:.1f}%)")
    
    logger.info(f"\n{'='*60}")
    logger.info("테스트 완료")
    logger.info(f"{'='*60}\n")
    
    return {
        "total_tests": total_tests,
        "correct_predictions": correct_predictions,
        "accuracy": accuracy,
        "results": all_results
    }


if __name__ == "__main__":
    try:
        results = run_validation_tests()
        
        # 최종 결과 출력
        print(f"\n{'='*60}")
        print(f"최종 정확도: {results['accuracy']:.1f}%")
        print(f"{'='*60}\n")
        
        if results['accuracy'] >= 80:
            print("✓ 검증 시스템이 우수한 성능을 보입니다!")
        elif results['accuracy'] >= 60:
            print("⚠ 검증 시스템이 양호한 성능을 보이지만 개선이 필요합니다.")
        else:
            print("✗ 검증 시스템의 성능이 부족합니다. 프롬프트 개선이 필요합니다.")
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
