# ai/standards_engine.py
# 2022 개정 국어 성취기준(고등) 간이 매핑 + 대화형 피드백 엔진
from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[1]
STD_PATH = ROOT / "report" / "ko_korean_2022_standards_min.json"

# ------- 로드 -------
with STD_PATH.open("r", encoding="utf-8") as f:
    STANDARDS: Dict[str, Any] = json.load(f)

# 간단 키워드 사전(질문/답안 → 성취기준 후보)
KEYWORDS = {
    "표현": ["비유", "은유", "직유", "대구", "반복", "표현", "수사"],
    "인물": ["인물", "성격", "심리", "행동", "변화"],
    "주제": ["주제", "주된", "핵심", "의미", "메시지"],
    "감상": ["감상", "느낌", "해석", "의도", "작가"],
    "설명": ["설명", "정의", "특징", "요점", "핵심어"],
    "논증": ["근거", "논거", "논리", "추론", "반론", "타당"],
    "말하기": ["발표", "토론", "말하기", "청중"],
}

# 기준ID → 키워드 그룹 간단 매핑(고등 국어 핵심 축약)
STANDARD_KEYMAP = {
    "K-HS-1": "표현",   # 문학 작품의 표현 효과 파악
    "K-HS-2": "인물",   # 등장인물/갈등/심리 분석
    "K-HS-3": "주제",   # 주제와 가치 탐구
    "K-HS-4": "감상",   # 다양한 관점 감상
    "K-HS-5": "설명",   # 설명/정보 조직·요약
    "K-HS-6": "논증",   # 논증의 타당성 평가
    "K-HS-7": "말하기", # 말하기/토론/발표 전략
}

def _pick_standard_by_text(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return STANDARDS["K-HS-3"]  # 기본: 주제

    # 키워드 일치 → 해당 그룹 기준 우선
    counts = {k: 0 for k in KEYWORDS.keys()}
    for group, kws in KEYWORDS.items():
        for kw in kws:
            if kw in text:
                counts[group] += 1

    # 가장 많이 일치한 그룹 찾기
    best_group: Optional[str] = None
    best_score = 0
    for g, c in counts.items():
        if c > best_score:
            best_group, best_score = g, c

    if best_group:
        # 그 그룹과 연결된 성취기준 중 하나 반환(여기선 1:1 매핑)
        for sid, g in STANDARD_KEYMAP.items():
            if g == best_group:
                return STANDARDS.get(sid, STANDARDS["K-HS-3"])

    return STANDARDS["K-HS-3"]


def analyze_question(username: str, question: str) -> Dict[str, Any]:
    std = _pick_standard_by_text(question)
    # 대화형 응답(간단 규칙 기반)
    answer = f"'{question}'에 대한 생각을 정리해 볼게요. {std['student_prompt']}"

    feedback = std["student_feedback"]
    teacher_tips = std["teacher_tips"]
    # 질문은 점수 없음 → 0
    return {
        "answer": answer,
        "feedback": feedback,
        "score": 0,
        "related_standard": {"id": std["id"], "title": std["title"]},
        "teacher_tips": teacher_tips,
    }


def analyze_essay(username: str, essay: str) -> Dict[str, Any]:
    std = _pick_standard_by_text(essay)

    # 단순 점수 휴리스틱: 길이 + 기준 키워드 포함
    base = min(100, max(30, len(essay) // 3))
    boost = 0
    for kw in KEYWORDS.get(SHORTHAND(std["id"]), []):
        if kw in essay:
            boost += 3
    score = max(50, min(100, base + boost))

    feedback = std["student_feedback"]
    if "근거" in essay or "예시" in essay:
        feedback += " 근거(예시)를 제시한 점이 좋아요. 다만, 문장 간 연결을 조금 더 분명히 해 보세요."

    teacher_tips = std["teacher_tips"]

    return {
        "answer": None,
        "feedback": feedback,
        "score": score,
        "related_standard": {"id": std["id"], "title": std["title"]},
        "teacher_tips": teacher_tips,
    }


def SHORTHAND(std_id: str) -> str:
    # "K-HS-3" → 해당 그룹 문자열
    return STANDARD_KEYMAP.get(std_id, "주제")
