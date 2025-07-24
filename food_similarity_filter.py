import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict

load_dotenv()

class FoodSimilarityFilter:
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
너는 음식 유사도 검증기야.
주어진 음식 데이터에서 기준 음식과 실제로 유사한 메뉴들만 남겨서 반환해줘.

중요 규칙:
- 같은 카테고리의 음식만 유지 (예: 면요리끼리, 밥요리끼리, 디저트끼리)
- 완전히 다른 종류의 음식은 제거 (예: 스파게티-샐러드, 떡볶이-피자)
- 유사한 조리법이나 재료를 사용하는 음식만 포함
- 점수가 높아도 음식 종류가 다르면 제거해야 함

음식 카테고리 예시:
- 면요리: 스파게티, 파스타, 짜장면, 짬뽕, 라면, 우동 등
- 밥요리: 비빔밥, 볶음밥, 김밥, 덮밥 등  
- 분식: 떡볶이, 순대, 튀김, 김밥 등
- 샐러드: 각종 샐러드류
- 디저트: 케이크, 아이스크림, 과일 등
- 한식: 불고기, 갈비, 김치찌개 등
- 중식: 짜장면, 짬뽕, 탕수육 등

입력 데이터: {food_data}

각 기준 음식에 대해 실제로 유사한 메뉴들만 남겨서 최종적으로 유효한 메뉴들의 리스트만 다음 JSON 형식으로 반환해:
{{
  "menu": ["유효한메뉴1", "유효한메뉴2", "유효한메뉴3"]
}}

예시:
입력: {{'스파게티': [{{'menu': '파스타', 'score': 0.99}}, {{'menu': '샐러드', 'score': 0.95}}], '비빔밥': [{{'menu': '산채 비빔밥', 'score': 0.84}}]}}
출력: {{"menu": ["파스타", "산채 비빔밥"]}}
(샐러드는 스파게티와 다른 카테고리이므로 제거, 유사한 메뉴들만 추출)
"""

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["food_data"]
        )

        # LLM 체인 구성
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            output_parser=self.output_parser,
            # verbose=True  # LLMChain의 verbose는 작동합니다
        )

    def filter_similar_foods(self, food_data: Dict) -> List[str]:
        # 딕셔너리를 문자열로 변환
        food_data_str = str(food_data)
        print(f"전송되는 음식 데이터: {food_data_str}")  # 디버깅용
        
        # LLM 체인 실행
        result = self.chain.run(food_data=food_data_str)
        print(f"LLM 응답: {result}")  # 디버깅용
        
        # 결과에서 menu 리스트만 반환
        return result.get("menu", [])