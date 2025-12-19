from .dialog_manager import detect_category

def analyze_essay(answer: str, base_category: str="") -> dict:
    cat = base_category or detect_category(answer)
    length = len(answer.strip())
    score = 60 + min(40, length // 20)  # 길이에 따른 간단 가산
    score = min(100, score)
    fb = {
        "화법": "도입-전개-정리 3단 구성을 지키고, 근거 예시는 2개 이내로 간결히 제시해 보세요.",
        "문학": "주제/배경/인물의 변화를 짧게 정리하고, 해석에는 작품 내 단서(시어, 대사)를 붙여 보세요.",
        "문법": "문장 성분을 괄호로 표시해 구조를 확인하고, 맞춤법/띄어쓰기는 국립국어원 기준으로 재검토하세요.",
        "일반": "답안을 화법/문학/문법 중 하나로 좁히고 개념-근거-예시를 순서대로 정리해 보세요."
    }[cat]
    return {"score": score, "category": cat, "feedback": fb}
