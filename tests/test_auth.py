import pytest

def test_register_success(client):
    """회원가입 성공 테스트"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser1", "password": "password123", "role": "student"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "회원가입 완료"

def test_register_duplicate_username(client):
    """중복 아이디 회원가입 실패 테스트"""
    # 첫 번째 가입
    client.post(
        "/api/auth/register",
        json={"username": "testuser2", "password": "password123", "role": "student"}
    )
    # 두 번째 동일한 아이디 가입 시도
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser2", "password": "password123", "role": "student"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "이미 존재하는 아이디입니다."

def test_login_success(client):
    """로그인 성공 테스트"""
    # 사용자 생성
    client.post(
        "/api/auth/register",
        json={"username": "loginuser", "password": "loginpass", "role": "student"}
    )
    # 로그인 시도
    response = client.post(
        "/api/auth/login",
        json={"username": "loginuser", "password": "loginpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["username"] == "loginuser"
    assert data["role"] == "student"

def test_login_fail(client):
    """로그인 실패 테스트 (잘못된 비밀번호)"""
    client.post(
        "/api/auth/register",
        json={"username": "wronguser", "password": "correctpass", "role": "student"}
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "아이디 또는 비밀번호가 올바르지 않습니다."
