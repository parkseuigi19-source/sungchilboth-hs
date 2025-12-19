import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

# ==========================================
# 1. State Definition
# ==========================================
class GraphState(TypedDict):
    question: str
    standard: str  # 성취기준
    rubric: str    # 채점 기준
    student_answer: str
    
    # Outputs
    analysis_result: Dict[str, Any] # 분석 결과 (JSON)
    mastery_level: str              # PASS, PARTIAL, FAIL
    feedback_text: str              # 학생용 피드백

# ==========================================
# 2. Nodes
# ==========================================

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def analyze_node(state: GraphState):
    """
    학생 답안을 분석하고 채점 기준에 따라 평가합니다.
    """
    print("--- 🔍 ANALYZING SUBMISSION ---")
    
    prompt = f"""
    당신은 고등학교 국어 교사입니다. 학생의 서술형 답안을 평가해주세요.
    
    [문제]
    {state['question']}
    
    [성취기준]
    {state['standard']}
    
    [채점 기준(Rubric)]
    {state['rubric']}
    
    [학생 답안]
    {state['student_answer']}
    
    다음 형식의 JSON으로만 응답하세요:
    {{
        "strengths": "학생 답안의 장점",
        "weaknesses": "학생 답안의 부족한 점",
        "missing_concepts": ["누락된 핵심 개념1", "누락된 핵심 개념2"],
        "logic_score": 8,
        "content_score": 7,
        "mastery_level": "PASS" | "PARTIAL" | "FAIL",
        "feedback_for_student": "학생에게 줄 친절하고 구체적인 피드백 (존댓말)"
    }}
    """
    
    response = llm.invoke([SystemMessage(content="JSON 형식으로 응답하세요."), HumanMessage(content=prompt)])
    
    try:
        result = json.loads(response.content)
    except:
        # Fallback if JSON parsing fails
        result = {
            "strengths": "",
            "weaknesses": "",
            "missing_concepts": [],
            "mastery_level": "PARTIAL",
            "feedback_for_student": response.content
        }
        
    return {
        "analysis_result": result,
        "mastery_level": result.get("mastery_level", "PARTIAL"),
        "feedback_text": result.get("feedback_for_student", "")
    }



# ==========================================
# 3. Conditional Logic
# ==========================================
def check_mastery(state: GraphState):
    if state["mastery_level"] == "PASS":
        return "pass"
    return "remedial"

# ==========================================
# 4. Graph Construction
# ==========================================
workflow = StateGraph(GraphState)

workflow.add_node("analyze", analyze_node)

workflow.set_entry_point("analyze")

workflow.add_edge("analyze", END)

# Compile
app_graph = workflow.compile()
