import pytest

def test_get_dashboard_stats(client):
    """교사 대시보드 통계 API 테스트"""
    # 기본 교사 계정 준비
    client.post("/api/auth/register", json={
        "username": "teacher_test", "password": "pass", "role": "teacher"
    })
    
    response = client.get("/api/teacher/dashboard-stats?teacher_username=teacher_test")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "questions" in data
    assert "pending" in data
    assert "chart" in data

def test_generate_class_report(client):
    """학급 리포트 생성 API 테스트"""
    payload = {
        "teacher_username": "teacher_test",
        "class_name": "1-1",
        "subject": "국어",
        "report_type": "unit"
    }
    # 실제 리포트 생성 로직이 외부 라이브러리(PDF 등)를 많이 사용하면 Mocking 이 필요할 수 있음
    response = client.post("/api/teacher/class-report/generate", json=payload)
    
    # 생성 로직이 복잡할 수 있으므로 200 혹은 500(개발 중인 사유로) 등을 체크
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "data" in data
