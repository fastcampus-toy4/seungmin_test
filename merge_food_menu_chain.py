from main_menu_selector import MainMenuSelector
from food_similarity_filter import FoodSimilarityFilter
from food_menu_matcher import FoodMenuMatcher
import json
from pypika import Query, Table
from mysql_connector import MYSQLConnector 

class MergeFoodMenuChain:
    def __init__(self):
        self.mainMenuSelector = MainMenuSelector()
        self.foodSimilarityFilter = FoodSimilarityFilter()
        self.foodMenuMatcher = FoodMenuMatcher()

    def ProcessMergeFoodMenuChain(self, restaurant_id_list: list, food_list: dict) -> dict:
        db = MYSQLConnector()
        # 음식점 id로 메뉴 받아오기
        restaurant = Table("restaurant")
        query = Query.from_(restaurant).select("*").where(restaurant.restaurant_id.isin(restaurant_id_list))
        menu_list = db.excute_query(query_obj=query)
        
        # 메뉴 이름 리스트
        menu_name_list = [menu["name"] for menu in menu_list if "name" in menu]

        # 음식 리스트를 JSON으로 파싱
        food_data = json.loads(food_list)
        # 음식 리스트의 recommended_foods에서 name만 뽑아 리스트로 저장
        food_name_list = [item['name'] for item in food_data['recommended_foods']]

        # 메뉴와 음식 유사도 검사
        # 추천할 메뉴 이름 리스트 반환
        result_menu_list = FoodMenuMatcher.get_recommendable_menus(food_name_list, menu_name_list)
        
        # 유사도 떨어지는 메뉴 한번 더 필터링
        filtered_menu_list = FoodSimilarityFilter.filter_similar_foods()
        
        # 추천할 메뉴 리스트에서 음료, 술 제외
        result_main_menu_list = MainMenuSelector.menuSelect(filtered_menu_list)

        # 최종 메뉴 이름 리스트로 메뉴 리스트 필터링
        final_menu_list = [menu for menu in menu_list if menu["name"] in result_main_menu_list]
        
        return final_menu_list