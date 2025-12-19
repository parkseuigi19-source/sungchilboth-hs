import os
import json
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from database import engine
from sqlalchemy.orm import Session
from models import Record

load_dotenv()

router = APIRouter(prefix="/api/agent", tags=["LangChain Agent"])

# ---------------------------
# ✅ 교육용 Tool 정의
# ---------------------------
@tool
def kor_curriculum_tool(query: str) -> str:
    """2022 개정 국어 성취기준 관련 설명을 제공합니다."""
    standards = {
        "문학": "문학 작품의 주제와 표현 방법을 이해한다.",
        "화법": "의사소통의 목적과 상황에 맞게 발화한다.",
        "작문": "쓰기 목적에 따라 내용을 조직하고 문단을 구성한다.",
        "문법": "품사와 문장 성분을 구별하고 문장을 분석한다.",
    }
    for key, val in standards.items():
        if key in query:
            return f"[{key}] {val}"
    return "관련 성취기준을 찾을 수 없습니다."


@tool
def study_feedback_tool(text: str) -> str:
    """학생의 학습 텍스트를 분석하고 피드백을 제공합니다."""
    if "논설문" in text or "주장" in text:
        return "주장과 근거의 논리적 연결을 강화해보세요."
    if "시" in text or "운율" in text:
        return "운율적 효과를 강조하여 감정 전달을 높여보세요."
    if "문법" in text:
        return "문장 구조를 분석하고 문장 성분 간 관계를 파악해보세요."
    return "핵심 내용과 문장 구조를 명확히 다듬으면 더 좋습니다."


# ---------------------------
# ✅ LangChain Agent 생성
# ---------------------------
model = ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True)
memory = InMemorySaver()
agent = create_react_agent(model=model, tools=[kor_curriculum_tool, study_feedback_tool], checkpointer=memory)


# ---------------------------
# ✅ FastAPI Endpoint (Streaming)
# ---------------------------
@router.post("/chat")
async def chat_with_agent(request: Request):
    data = await request.json()
    message = data.get("message", "")
    thread_id = data.get("thread_id", "student-1")

    async def event_stream():
        try:
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]},
                {"configurable": {"thread_id": thread_id}},
            )
            output = result["messages"][-1].content
            for ch in output:
                yield f"data: {json.dumps({'token': ch})}\n\n"
                await asyncio.sleep(0.02)
            
            # ✅ 활동 기록 저장
            try:
                db = Session(bind=engine)
                new_record = Record(
                    username=thread_id,
                    question=message,
                    reply=output,
                    category="AI 채팅",
                    score=0.0
                )
                db.add(new_record)
                db.commit()
                db.close()
            except Exception as db_err:
                print(f"채팅 기록 저장 오류: {db_err}")

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
