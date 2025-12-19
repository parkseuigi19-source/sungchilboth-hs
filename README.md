# 성취봇-HS (Seongchibot-HS)

**2022 개정 교육과정 반영 맞춤형 학습 지원 시스템**

성취봇-HS는 학생들의 성취 기준 달성을 돕고, 교사들에게는 효율적인 학습 관리 및 평가 도구를 제공하는 AI 기반 학습 지원 플랫폼입니다.

## 🌟 주요 기능

### 👨‍🎓 학생용
- **AI 튜터 채팅**: LangChain & OpenAI GPT-4o 기반의 실시간 학습 질의응답
- **성취도 대시보드**: 개인별 학습 현황 및 성취율 시각화
- **E-포트폴리오**: 학습 이력 및 결과물 자동 정리
- **셀프 채점**: 서술형/논술형 답안에 대한 AI 자동 채점 및 피드백

### 👩‍🏫 교사용
- **학급 리포트**: 반 전체의 학습 현황 및 성취도 분석 보고서
- **일괄 채점**: 학생 답안 일괄 처리 및 분석
- **AI 보조 도구**: 수업 자료 생성 및 평가 기준 관리 지원

## 🛠 기술 스택 (Tech Stack)

### Backend
- **Python 3.9+**
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Pydantic**: 데이터 검증

### AI & LLM
- **LangChain**: LLM 어플리케이션 개발 프레임워크
- **OpenAI API (GPT-4o)**: 교육용 챗봇 및 평가 엔진
- **LangGraph**: 에이전트 워크플로우 관리

### Frontend
- **Jinja2 Templates**: 서버 사이드 렌더링
- **Vanilla JS / CSS**: 사용자 인터페이스 구현
- **Matplotlib**: 데이터 시각화 및 리포트 그래프 생성

### Infrastructure & Tools
- **Docker & Docker Compose**: 컨테이너 기반 배포
- **SQLite / MySQL**: 데이터베이스 (환경에 따라 구성)

## 📂 디렉토리 구조

```
sungchilboth-hs-main/
├── ai/                  # AI 핵심 로직 (분석기, 채점기, 에이전트 등)
├── api/                 # FastAPI 라우터 (기능별 API 분리)
├── docs/                # 문서 관련 파일
├── report/              # 리포트 생성 결과물 저장
├── static/              # 정적 파일 (CSS, JS, 이미지)
├── templates/           # HTML 템플릿 (Jinja2)
├── tests/               # 단위 테스트 및 테스트 데이터
├── utils/               # 유틸리티 함수
├── main.py              # 메인 애플리케이션 진입점
├── models.py            # 데이터베이스 모델 정의
├── database.py          # DB 연결 설정
├── seed_db.py           # 초기 데이터 적재 스크립트
├── requirements.txt     # 의존성 패키지 목록
└── docker-compose.yml   # Docker 실행 설정
```

## 🚀 시작하기 (Getting Started)

### 사전 요구 사항 (Prerequisites)
- Python 3.9 이상
- Docker & Docker Compose (선택 사항)
- OpenAI API Key

### 1. 환경 설정 (.env)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 작성하세요.

```env
OPENAI_API_KEY=sk-your-api-key-here
DB_URL=sqlite:///./sungchibot.db
```

### 2. 로컬 실행 (Local Execution)

패키지 설치:
```bash
pip install -r requirements.txt
```

서버 실행:
```bash
python main.py
# 또는
uvicorn main:app --reload
```

브라우저에서 `http://localhost:8000` 접속

### 3. Docker 실행

```bash
docker-compose up --build -d
```


