import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 환경 변수 로드
load_dotenv()

class StandardsMatcher:
    def __init__(self, standards_file: str = "achievement_standards.json"):
        self.standards_file = standards_file
        self.standards_data = self._load_standards()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def _load_standards(self) -> List[Dict[str, Any]]:
        try:
            with open(self.standards_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("standards", [])
        except Exception as e:
            print(f"Error loading standards: {e}")
            return []

    def match(self, question: str, essay: str) -> Dict[str, Any]:
        """
        질문과 답안을 기반으로 가장 적합한 성취기준을 매칭합니다.
        """
        # 디버깅을 위해 매번 파일 로드 (변경사항 즉시 반영)
        self.standards_data = self._load_standards()
        
        text = f"{question} {essay}".lower()
        print(f"--- [StandardsMatcher] Matching text: {text} ---")
        print(f"--- [StandardsMatcher] Total standards loaded: {len(self.standards_data)} ---")
        
        # 1. 단순 키워드 매칭 (빠른 속도)
        for std in self.standards_data:
            keywords = std.get("keywords", [])
            for k in keywords:
                if k.lower() in text:
                    print(f"--- [StandardsMatcher] Keyword '{k}' matched standard: {std['code']} ---")
                    return std

        # 2. LLM 매칭 (정교함)
        print("--- [StandardsMatcher] No keyword match. Trying LLM... ---")
        return self._match_with_llm(question, essay)

    def _match_with_llm(self, question: str, essay: str) -> Dict[str, Any]:
        """GPT-4o를 사용하여 가장 적합한 성취기준 코드 추출"""
        
        # 성취기준 목록 요약
        standards_summary = "\n".join([
            f"- [{s['code']}] {s['desc']}" 
            for s in self.standards_data
        ])

        prompt = f"""
        당신은 대한민국 고등학교 국어 교사입니다. 다음 학생의 답안 내용과 가장 관련이 깊은 '2022 개정 국어과 성취기준' 하나를 선택하세요.
        
        [학생이 보고 있는 질문/발문]
        {question if question else '없음 (일반적인 문장 분석)'}
        
        [학생의 서술형 답안/텍스트]
        {essay}
        
        [후보 성취기준 목록]
        {standards_summary}
        
        가장 적절한 한 명의 성취기준 코드를 골라 아래 JSON 형식으로만 답하세요.
        정확히 'matched_code' 필드만 포함해야 합니다.
        
        {{
            "matched_code": "코드입력"
        }}
        
        만약 관련성을 전혀 찾을 수 없다면 {{"matched_code": "K-HS-?"}}를 반환하세요.
        """

        try:
            response = self.llm.invoke([
                SystemMessage(content="교육과정 전문가로서 성취기준 코드를 정확히 매칭하세요. JSON 형식만 출력하세요."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content.strip()
            # 마크다운 제거
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:].strip()
            
            result = json.loads(content)
            matched_code = result.get("matched_code")
            print(f"--- [StandardsMatcher] LLM matched code: {matched_code} ---")

            # 코드에 해당하는 데이터 전체 반환
            for std in self.standards_data:
                if std["code"] == matched_code:
                    return std
        except Exception as e:
            print(f"--- [StandardsMatcher] LLM Match Error: {str(e)} ---")

        return {
            "code": "K-HS-?",
            "domain": "일반",
            "desc": "관련 성취기준을 명확히 찾을 수 없습니다."
        }

# 싱글톤 인스턴스
matcher = StandardsMatcher()
