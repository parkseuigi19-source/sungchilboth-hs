import pytest

def test_agent_chat(client):
    """AI 에이전트 채팅 API 테스트 (StreamingResponse 대응)"""
    payload = {
        "username": "chat_user",
        "message": "안녕, 오늘 뭘 배울 수 있어?"
    }
    # StreamingResponse를 테스트하기 위해 stream=True 옵션 사용 또는 직접 읽기
    response = client.post("/api/agent/chat", json=payload)
    
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # 스트리밍 데이터의 일부가 오는지 확인 (간단하게 비어있지 않은지만 체크)
    content = response.text
    assert "data:" in content

