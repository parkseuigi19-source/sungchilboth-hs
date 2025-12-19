import requests
import json

def test_analyze():
    url = "http://localhost:8000/api/student/analyze"
    payload = {
        "username": "student1",
        "question": "",
        "essay": "비가 온다는 날씨 표현을 문장입니다."
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_analyze()
