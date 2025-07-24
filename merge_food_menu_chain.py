from main_menu_selector import MainMenuSelector
from food_similarity_filter import FoodSimilarityFilter
from food_menu_matcher import FoodMenuMatcher
import json

class MergeFoodMenuChain:
    def __init__(self):
        self.mainMenuSelector = MainMenuSelector()
        self.foodSimilarityFilter = FoodSimilarityFilter()
        self.foodMenuMatcher = FoodMenuMatcher()

    def ProcessMergeFoodMenuChain(self, menu_list: dict, food_list: dict) -> dict:
        # 1) 원본 파라미터를 JSON으로 파싱
        food_data = json.loads(food_list)
        # 2) recommended_foods에서 name만 뽑아 리스트로
        food_names = [item['name'] for item in food_data['recommended_foods']]

        # 메뉴와 음식 유사도 검사
        # 추천할 메뉴 리스트 반환
        resultFoods = FoodMenuMatcher.get_recommendable_menus(food_names=food_names, menu_names=menu_list)
        
        # 추천할 메뉴 리스트에서 음료, 술 제외
        resultMainMenu = MainMenuSelector.menuSelect(resultFoods)

        # 
        