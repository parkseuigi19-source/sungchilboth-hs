# 성취봇-HS (SungchiBot-HS) 🎓

> **2022 개정 교육과정 기반 고교학점제 지원 AI 밀착 학습 및 평가 시스템**

성취봇-HS는 고등학교 교사의 업무를 경감하고, 학생들에게는 개별화된 맞춤형 피드백을 제공하기 위해 개발된 **AI 하이브리드 학습 지원 플랫폼**입니다. 생성형 AI(GPT-4o)를 활용하여 서/논술형 문항 자동 채점, 개인별 성취 분석 리포트 생성, 1:1 학습 튜터링을 제공합니다.

## 📂 프로젝트 문서 (Project Documentation)

이 프로젝트의 상세한 기획 및 기술 명세는 아래 문서들을 참고해 주세요.

- **[📌 프로젝트 정의서 (Project Definition)](docs/PROJECT_DEFINITION.md)**
  - 기획 배경, 개발 목적, 해결하고자 하는 문제, 기대 효과 등 프로젝트의 전반적인 개요를 다룹니다.

- **[✅ MVP 기능 정의서 (Feature Specs)](docs/MVP_FEATURES.md)**
  - 학생, 교사, 관리자별 핵심 기능 명세와 필수 개발 요구사항을 정의합니다.

- **[🛠 기술 스택 정의서 (Tech Stack)](docs/TECH_STACK.md)**
  - Backend(FastAPI), Frontend(Modern Web), AI(LangChain), DB 등 사용된 기술과 선정 이유를 설명합니다.

- **[🏗 시스템 아키텍처 (Architecture)](docs/SYSTEM_ARCHITECTURE.md)**
  - 시스템 구성도, 데이터 흐름, 모듈별 역할 등 기술적인 설계 내용을 포함합니다.

---

## 🚀 시작하기 (Quick Start)

### 필수 요구사항
- Python 3.12+
- OpenAI API Key

### 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone https://github.com/your-repo/sungchibot-hs.git
   cd sungchibot-hs
   ```

2. **가상환경 설정**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**
   `.env.example` 파일을 복사하여 `.env` 생성 후 API Key 입력
   ```bash
   cp .env.example .env
   ```

5. **서버 실행**
   ```bash
   python main.py
   ```
   브라우저에서 `http://localhost:8000` 접속

---

## 📜 라이선스
This project is licensed under the MIT License.
