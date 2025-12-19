# 기술 스택 정의서 (Tech Stack Definition)

## 1. 개요
본 프로젝트는 확장성(Scalability)과 유지보수성(Maintainability)을 최우선으로 고려하여 **FastAPI + Modern Web** 기반으로 설계되었습니다.

## 2. 전체 기술 스택 요약
| 분류 | 기술명 | 버전 | 용도 |
| :--- | :--- | :--- | :--- |
| **Backend** | Python | 3.12+ | 메인 프로그래밍 언어 |
| | FastAPI | 0.100+ | 고성능 비동기 웹 프레임워크 |
| | Uvicorn | latest | ASGI 웹 서버 |
| **Frontend** | HTML5 / CSS3 | - | 웹 표준 구조 및 스타일링 |
| | Jinja2 | latest | 서버 사이드 템플릿 엔진 |
| | TailwindCSS | CDN | 유틸리티 퍼스트 CSS 프레임워크 |
| | JavaScript (ES6+) | - | 클라이언트 동적 기능 구현 |
| **Database** | SQLite | 3.x | 경량 관계형 데이터베이스 (개발용) |
| | SQLAlchemy | 2.0+ | Python ORM |
| | Pydantic | 2.0+ | 데이터 유효성 검사 및 설정 관리 |
| **AI / ML** | OpenAI GPT-4o | - | 생성형 AI 모델 (채점, 첨삭, 챗봇) |
| | LangChain | latest | LLM 애플리케이션 프레임워크 |
| **DevOps** | Git / GitHub | - | 버전 관리 및 협업 |
| **Tools** | ReportLab | latest | PDF 리포트 생성 및 커스터마이징 |
| | Matplotlib | latest | 성취도 데이터 시각화 및 차트 생성 |

## 3. 기술 선정 배경

### 가. Backend (FastAPI)
- **선정 이유**: Python 기반의 비동기 처리가 용이하며, 자동 문서화(Swagger UI) 기능을 제공하여 API 개발 생산성이 높음. Pydantic을 이용한 강력한 타입 체크로 안정성 확보.
- **주요 활용**: RESTful API 서버, 웹 페이지 렌더링, AI 모델 서빙 등.

### 나. AI (LangChain + GPT-4o)
- **선정 이유**: 복잡한 추론이 필요한 서수/논술형 채점 및 구조화된 피드백 생성을 위해 성능이 입증된 GPT-4o 활용. LangChain을 통해 프롬프트 관리 및 체이닝 구현 용이.
- **주요 활용**: 문제 자동 채점, 오개념 분석, 1:1 맞춤형 학습 튜터, 문제 생성.

### 다. Report Generation (ReportLab)
- **선정 이유**: HTML to PDF 방식보다 정밀한 레이아웃 제어가 가능하며, 서버 사이드에서 고품질 인쇄용 리포트를 생성하는 데 적합.
- **주요 활용**: 학생용 포트폴리오 PDF, 교사용 학급 분석 리포트 PDF 생성.

### 라. Frontend (TailwindCSS)
- **선정 이유**: 별도의 CSS 파일 관리 없이 클래스명 조합만으로 빠른 UI 개발 가능. 모던하고 일관된 디자인 시스템 구축 용이. CDN 방식을 통해 별도 빌드 과정 없이 가볍게 도입.
