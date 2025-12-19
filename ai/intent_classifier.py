def classify_intent(text: str) -> str:
    q_words = ["?", "무엇", "왜", "어떻게", "언제", "누가"]
    if any(word in text for word in q_words):
        return "question"
    if any(text.endswith(ending) for ending in ["다", "습니다", "에요", "예요", "입니다"]):
        return "answer"
    return "other"
