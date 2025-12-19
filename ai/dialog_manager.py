# 간단한 규칙 기반(오프라인). OpenAI 없이 동작
def detect_category(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["화법", "발표", "토론", "대화"]): return "화법"
    if any(k in t for k in ["문학", "소설", "시", "희곡", "수필"]): return "문학"
    if any(k in t for k in ["문법", "품사", "문장성분", "어미", "활용"]): return "문법"
    return "일반"

def generate_context_reply(question: str, context: str="") -> dict:
    cat = detect_category(question)
    # 아주 간단한 답변 템플릿
    core = {
        "화법": "의사소통 상황과 목적을 먼저 파악하고, 주장-근거-예시 순으로 구성해 보세요.",
        "문학": "작품의 배경·인물·주제로 핵심을 잡고, 인용은 짧게, 해석은 구체적으로 적어보세요.",
        "문법": "품사와 문장성분을 구분하고, 어미와 연결어미의 기능을 구체 예로 확인하세요.",
        "일반": "질문을 조금 더 구체화하면 더 정확히 도와줄 수 있어요."
    }[cat]
    return {"reply": core, "category": cat}
