from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import pandas as pd

class FoodMenuMatcher:
    def __init__(self, model_name='jhgan/ko-sroberta-multitask'):
        """
        한국어 특화 임베딩 모델을 사용한 음식-메뉴 매처

        Args:
            model_name: 사용할 sentence transformer 모델
                      - 'jhgan/ko-sroberta-multitask': 한국어 특화 모델 (추천)
                      - 'sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens': 다국어 모델
        """
        print(f"임베딩 모델 로딩 중: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("모델 로딩 완료!")

    def calculate_similarity_matrix(self, food_names: List[str], menu_name_list: List[str]) -> np.ndarray:
        """
        음식 이름과 메뉴 이름 간의 유사도 매트릭스 계산

        Args:
            food_names: 음식 이름 리스트
            menu_names: 메뉴 이름 리스트

        Returns:
            similarity_matrix: (len(food_names), len(menu_names)) 크기의 유사도 매트릭스
        """
        print("임베딩 생성 중...")

        # 임베딩 생성
        food_embeddings = self.model.encode(food_names, show_progress_bar=True)
        menu_embeddings = self.model.encode(menu_name_list, show_progress_bar=True)

        # 코사인 유사도 계산
        similarity_matrix = cosine_similarity(food_embeddings, menu_embeddings)

        print(f"유사도 계산 완료: {similarity_matrix.shape}")
        return similarity_matrix

    def find_matches(self,
                    food_names: List[str],
                    menu_name_list: List[str],
                    threshold: float = 0.7,
                    top_k: int = 100) -> List[Dict]:
        """
        유사도 기반 매칭 수행

        Args:
            food_names: 음식 이름 리스트
            menu_names: 메뉴 리스트
            threshold: 유사도 임계값 (0.0 ~ 1.0)
            top_k: 각 음식당 반환할 최대 메뉴 개수

        Returns:
            matches: 매칭 결과 리스트
        """
        
        # 유사도 매트릭스 계산
        similarity_matrix = self.calculate_similarity_matrix(food_names, menu_name_list)

        matches = []

        for i, food_name in enumerate(food_names):
            # 해당 음식에 대한 모든 메뉴의 유사도
            food_similarities = similarity_matrix[i]

            # 임계값 이상의 메뉴들 찾기
            valid_indices = np.where(food_similarities >= threshold)[0]

            if len(valid_indices) > 0:
                # 유사도 높은 순으로 정렬
                sorted_indices = valid_indices[np.argsort(food_similarities[valid_indices])[::-1]]

                # top_k개만 선택
                top_indices = sorted_indices[:top_k]

                for j in top_indices:
                    matches.append({
                        'food_name': food_name,
                        'menu_name': menu_name_list[j],
                        'similarity_score': float(food_similarities[j]),
                        'food_index': i,
                        'menu_index': j
                    })

        # 전체적으로 유사도 높은 순으로 정렬
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)

        return matches

    def get_recommendable_menus(self,
                               food_name_list: List[str],
                               menu_name_list: List[str],
                               threshold: float = 0.7,
                               top_k: int = 100) -> Dict:
        """
        추천 가능한 메뉴 목록 반환 (LLM 입력용)

        Returns:
            result: {
                'matches': 매칭 결과,
                'summary': 요약 정보,
                'menu': 후보 메뉴 리스트
            }
        """
        matches = self.find_matches(food_name_list, menu_name_list, threshold, top_k)

        # 고유한 메뉴 이름만 추출
        unique_menu_name_list = list({match['menu_name'] for match in matches})

        # 음식별 매칭 요약
        food_summary = {}
        for match in matches:
            food = match['food_name']
            if food not in food_summary:
                food_summary[food] = []
            food_summary[food].append({
                'menu': match['menu'],
                'score': match['similarity_score']
            })

        result = {
            'matches': matches,
            'food_summary': food_summary,
            'menu': unique_menu_name_list,
            'total_matches': len(matches),
            'unique_menus': len(unique_menu_name_list)
        }

        return result