# 시스템 아키텍처 (System Architecture)

## 1. 시스템 구조도 (System Architecture Diagram)

```mermaid
graph TD
    User[Client (Browser)] -- HTTP/HTTPS --> LB[Load Balancer / Proxy]
    LB --> WebApp[FastAPI Application Server]
    
    subgraph "Application Layer"
        WebApp --> Auth[Authentication Module]
        WebApp --> Core[Core Logic (Assessment/Grading)]
        WebApp --> PDF[PDF Generation Service]
        WebApp --> AIService[AI Agent Service (LangChain)]
    end
    
    subgraph "Data Layer"
        Core -- ORM --> DB[(SQLite Database)]
        AIService -- API Call --> OpenAI[OpenAI API (GPT-4o)]
    end

    subgraph "Output"
        PDF -- Generate --> FileSystem[File System (Reports)]
    end
```

## 2. 모듈별 상세 설명

### 가. Client Layer
- **구성**: PC 및 모바일 웹 브라우저.
- **기능**: 사용자 인터페이스 제공, 사용자 입력 값 전달, 서버 응답 시각화.
- **특징**: 반응형 웹 디자인(Responsive Web Design) 적용으로 다양한 디바이스 지원.

### 나. Application Layer (FastAPI)
1. **API Router**: 요청 URL에 따라 적절한 컨트롤러로 라우팅.
    - `/api/auth`: 로그인, 회원가입 등 인증 처리.
    - `/api/student`: 학생 전용 기능 (문제 풀이, 조회).
    - `/api/teacher`: 교사 전용 기능 (채점, 관리).
    - `/api/report`: 리포트 생성 요청 처리.
2. **AI Service**: LangChain을 활용하여 OpenAI API와 통신. 프롬프트 엔지니어링이 적용된 체인(Chain)을 통해 고품질 응답 생성.
3. **PDF Service**: 데이터베이스의 통계 정보를 시각화(Chart)하고 리포트 양식에 맞춰 PDF 파일 렌더링.

### 다. Data Layer
- **SQLite**: 사용자 정보, 문항 데이터, 채점 결과, 학습 이력 등 영구 데이터 저장.
- **Schema Design**:
    - `User`: 사용자 기본 정보 및 권한.
    - `Class`: 학급 및 소속 정보.
    - `Assignment/Question`: 과제 및 문항 정보.
    - `Submission/Feedback`: 학생 답안 및 AI 피드백 결과.

## 3. 데이터 흐름 (Data Flow) - 채점 프로세스 예시
1. **제출(Submit)**: 학생이 웹 화면에서 답안 작성 후 제출.
2. **저장(Save)**: `Submission` 테이블에 답안 텍스트 저장.
3. **분석(Analyze)**: 백그라운드 태스크 또는 동기 요청으로 AI Agent 호출.
    - 답안, 정답, 루브릭을 LLM에 전송.
4. **결과 생성(Result)**: LLM이 점수 및 피드백 JSON 반환.
5. **피드백 저장(Persist)**: `Feedback` 테이블에 결과 저장.
6. **조회(Retrieve)**: 교사가 대시보드에서 채점 결과 확인 및 검수.
