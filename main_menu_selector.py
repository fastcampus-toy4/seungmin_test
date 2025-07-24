import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict

load_dotenv()

class MainMenuSelector:
    def __init__(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=OPENAI_API_KEY
        )
        # JSON 형식의 응답을 바로 파싱해 주는 OutputParser
        self.output_parser = JsonOutputParser()

        # 프롬프트 템플릿 수정 - 더 명확하게
        template = """
너는 음식 분류기야.
아래 메뉴 목록에서 음료와 술을 제외한 모든 음식들을 찾아서 반환해줘.

중요: 
- 음료(콜라, 사이다, 주스 등)는 제외
- 술(소주, 맥주, 와인, 막걸리 등)은 제외  
- 나머지 모든 음식은 포함해야 함
- 리스트에 있는 음식만 사용해야 함
- 파스타, 스파게티, 샐러드 등은 모두 음식이므로 포함

메뉴 목록: {menu}

반드시 다음 JSON 형식으로 답변해:
{{
  "menu": ["음식1", "음식2", "음식3"]
}}

예시1:
입력: 짜장면, 짬뽕, 탕수육, 콜라, 소주
출력: {{"menu": ["짜장면", "짬뽕", "탕수육"]}}

예시2:  
입력: 파스타, 스파게티, 샐러드, 콜라, 와인
출력: {{"menu": ["파스타", "스파게티", "샐러드"]}}
"""
        
        self.prompt = PromptTemplate(
            template=template, 
            input_variables=["menu"]
        )

        # LLM 체인 구성
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            output_parser=self.output_parser,
            # verbose=True  # LLMChain의 verbose는 작동합니다
        )

    def menuSelect(self, menu: List[str]) -> Dict[str, List[str]]:
        # 리스트를 문자열로 변환
        menu_str = ", ".join(menu)
        print(f"전송되는 메뉴: {menu_str}")  # 디버깅용
        
        # 올바른 타입으로 수정
        result: Dict[str, List[str]] = self.chain.run(menu=menu_str)
        print(f"LLM 응답: {result}")  # 디버깅용
        return result