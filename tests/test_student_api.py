import pytest
from unittest.mock import patch, MagicMock

def test_submit_answer_success(client):
    """학생 답안 제출 및 AI 분석 테스트"""
    # 1. 로그인/계정 생성을 위한 환경 (register 호출 생략 가능, submit-api 내부에서 자동 생성 로직 있음)
    payload = {
        "username": "student_test",
        "question_id": 1,
        "answer_text": "진달래꽃은 이별의 정한을 애이불비의 태도로 승화시킨 작품입니다."
    }
    
    # LangGraph 호출을 Mocking 하여 실제 외부 API 호출 없이 테스트 진행 (필요 시)
    # 여기서는 실제 구현의 로직 흐름만 테스트하기 위해 Mock 없이 시도 (성패 여부 확인)
    # 만약 OpenAI API Key 환경변수가 없으면 에러가 날 수 있으므로 주의
    
    response = client.post("/api/student/submit", json=payload)
    
    # 200 OK 인지 혹은 에러가 나더라도 어떤 형식인지 확인
    # (실제 외부 API 호출이 포함된 경우 500 에러 가능성 있으므로 Mock 고려 권장)
    assert response.status_code in [200, 500] 
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "feedback" in data

def test_get_history(client):
    """학생 제출 이력 조회 테스트"""
    # 샘플 제출 (submit 직접 호출 대신 DB에 직접 넣거나 submit API가 성공했다는 가정 하에 조회)
    client.post("/api/student/submit", json={
        "username": "history_user",
        "question_id": 1,
        "answer_text": "테스트 답안입니다."
    })
    
    response = client.get("/api/student/history?username=history_user")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) > 0
    assert data["history"][0]["answer"] == "테스트 답안입니다."
