import requests
import json
import os
from typing import Dict, Optional, Tuple, List
from dotenv import load_dotenv
from config import Config
from utils.googleplacesAPI import GooglePlacesAPI
from utils.localLandmarkSearch import LocalLandmarkSearch
import numpy as np
from scipy.spatial import KDTree
# 載入環境變數
# load_dotenv('config.env')

# 載入環境變數
load_dotenv('../config.env')

class LandmarkSearch:
    def __init__(self):
        self.landmark_cache = {}
        self.shap_data_store={}
        
    def search_landmarks(self, lat: float, lon: float, case_id: str, form_type: str) -> Dict:
        print(f"[DEBUG] search_landmarks() 被執行, lat={lat}, lon={lon}, case_id={case_id}, form_type={form_type}")
        
        """搜索所有地標並計算距離"""
        self.found_types = set()
        google_places = GooglePlacesAPI()
        local_search= LocalLandmarkSearch()
        results = {
            'case_id': case_id,
            'form_type': form_type,
            'LAT': lat,
            'LON': lon,
            'Qitem': []
        }
        ## 遍歷LANDMARK_TYPES
        for case_type, type_info in Config.LANDMARK_TYPES.items():  ##case_type:"001", "002"...; type_info={'name', 'case_kind', 'cases'..}
            case_result = {
                'case_type': case_type,
                'case_kind': type_info['case_kind'],
                'case_name': type_info['name'],
                'score': None,
                'items': []
            }
            try:
                valid_landmarks = []
                landmarks=[]
                #local_landmarks=[]
                # 遍歷每個 case
                for case in type_info['cases']:
                    print(f"[DEBUG] case_type: {case_type}, case: {case}")
                    
                    search_method_type = case['search_methods']['type']
                    found_in_nearby = False
                    
                    # 處理 nearby 搜尋
                    if (search_method_type=='nearby_only' or search_method_type =='nearby_first'):
                        if 'nearby' in case['search_methods']:
                            nearby_params = case['search_methods']['nearby']['params']
                            search_params = {
                                "latitude":lat,
                                "longitude":lon,
                                "radius":case['distance'],
                                "included_types":nearby_params['includedTypes'],
                            }
                            if "includedPrimaryTypes" in nearby_params:
                                search_params.update({
                                    "includedPrimaryTypes": nearby_params['includedPrimaryTypes']
                                })
                            if "excludedPrimaryTypes" in nearby_params:
                                search_params.update({
                                    "excludedPrimaryTypes": nearby_params['excludedPrimaryTypes']
                                })
                            nearby_results = google_places.nearby_search(**search_params)
                            
                            print("[DEBUG] nearby_search() 回傳:", nearby_results)
                            if nearby_results and 'places' in nearby_results:  # 確保 'places' 存在
                                #print("places count:", len(nearby_results['places']))
                                for place in nearby_results['places']:
                                    data_store1= {
                                            'case_type': case_type,
                                            'case_kind':type_info['case_kind'],
                                            'place_id': place['id'],
                                            'destination': "place_id:"+place['id'],
                                            'name': place['displayName']['text'],
                                            'radius': None,
                                            'feature_types': case['case_type']
                                        }

                                    ## 各類商店市集包含一般小型超市~
                                    if case_type == "005" and case['case_type']== "各類商店市集" :
                                        if any(s not in ['超級市場', "居家用品店", "商店", "百貨公司"] for s in place['primaryTypeDisplayName']['text']):
                                               continue
                                        if any(s not in ["全聯", "家樂福", "寶雅", "小北", "迪卡儂", "光南", "五金","燦坤","宜得利", "特力屋", "HOLA"] for s in place['displayName']['text']):
                                            continue

                                    if case_type== "006" and case['case_type'] == "學校":
                                        if any(s not in ['小學', "大專院校", "高中", "大學", "國中"] for s in  place['primaryTypeDisplayName']['text']):
                                            continue
                                        if any(s in ["補習班", "美語", "文理", "教室", "文教", "補習", "美語", "外語", "安親", "公司","活動中心", "停車場","幼兒","留學", "代辦", "中心", "工作室", "教室","機構","演藝廳", "何嘉仁"]for s in place['displayName']['text']):
                                            continue
                                        if any(s not in ['國民小學', "中學", "中小學", "中等學校", "專科學校", "陸軍", "國際學校", "高中", "大學", "國中", "技術學院", "科技大學","國立","市立", "學校","高工", "家商","職業學校", "學校", "實驗","進修推廣", "美國學校", "特殊教育"] for s in place['displayName']['text']):
                                            continue

                                    if case_type == "007" and case['case_type']== "公園" :
                                        if any(s not in ["公園"] for s in place['displayName']['text']):
                                            continue

                                    if case_type == '014' and case['case_type']=='遊藝場':
                                        if place['addressComponents']['types']=='subpremise':  ## 在樓層裡面的不算
                                            continue
                                            
                                    print("Adding nearby landmarks to landmarks1:", data_store1)
                                    landmarks.append(data_store1)
                     # 處理 autocomplete 搜尋
                    if (search_method_type == 'autocomplete_only' or 
                        (search_method_type == 'nearby_first' and not found_in_nearby)):
                            
                        ## any outcomes 
                        if 'autocomplete' in case['search_methods']:
                            auto_params = case['search_methods']['autocomplete']['params']
                            auto_results = google_places.autocomplete_search(
                                input_text=auto_params['input'],
                                latitude=lat,
                                longitude=lon,
                                radius=case['distance'],
                                included_types=auto_params['includedTypes']
                            )
                            
                            print("[DEBUG] autocomplete_search() 回傳:", auto_results)
                            if auto_results:
                                for prediction in auto_results['suggestions']:

                                    ## 篩選傳統市場不能包含旁邊的小吃店跟餐廳
                                    if case_type == "005" and case['case_type'] =='傳統市場':
                                        if any(s in ["restaurant", "deli","store", "food","food_store"] for s in prediction['placePrediction']['types']):
                                            continue
                                        if all(s not in ["point_of_interest","market","establishment"] for s in prediction['placePrediction']['types']):
                                            continue
                                        if all(s not in ["point_of_interest","tourist_attraction", "market","establishment"] for s in prediction['placePrediction']['types']):
                                            continue
                                        
                                    if case_type == "005" and case['case_type'] =="超級市場":
                                        if '超市' in prediction['placePrediction']['text']['text']:  ##名子有超市不行 (家樂福超市)
                                            continue
                                        if any(s not in ['好市多', "愛買", "家樂福", "大潤發", "大買家"]  for s in prediction['placePrediction']['text']['text']):
                                             continue
                                        if any(s in ["restaurant", "deli","parking"] for s in prediction['placePrediction']['types']):  ## 餐廳/停車場等附屬設施也不行
                                            continue

                                    if case_type == "020" and case['case_type']=='垃圾場':
                                        if any(s in ['管辦大樓', '辦公大樓'] for s in prediction['placePrediction']['text']['text']):
                                            continue
                                    
                                    data_store = {
                                        'case_type': case_type,
                                        'case_kind':type_info['case_kind'],
                                        'place_id': prediction['placePrediction']['placeId'],
                                        'destination': "place_id:"+prediction['placePrediction']['placeId'],
                                        'name': prediction['placePrediction']['text']['text'],
                                        'radius': None,
                                        'feature_types': case['case_type']
                                    }
                                    print("Adding auto landmarks to landmarks:", data_store)
                                    if data_store:
                                        landmarks.append(data_store)
                                        
                    if search_method_type == 'local_only':
                        local_results = local_search.find_nearby_landmarks(
                            lat=lat,
                            lon=lon,
                            radius_km=case['distance']/1000,
                            target_case_type=case['case_type']
                        )
                        
                        print("[DEBUG] local_search.find_nearby_landmarks() 回傳:", local_results)
                        
                        if local_results:
                            for result in local_results:
                                data_store={
                                    "case_type": case_type,
                                    'case_kind':type_info['case_kind'],
                                    "place_id": result['place_id'],
                                    "destination": "{},{}".format(result['latitude'], result['longitude']),
                                    "name":result['name'],
                                    "radius":None,
                                    "feature_types":result['feature_types']
                                }
                                if data_store:
                                    print("Adding local landmarks to landmarks:", data_store)
                                    landmarks.append(data_store)
                    elif search_method_type=='shap_only':
                        shap_results = local_search.find_point_by_shap(
                            latitude=lat,
                            longitude=lon
                        )
                        
                        print("[DEBUG] find_point_by_shap() 回傳:", shap_results)
                        ## 鐵軌道路50公尺內
                        if shap_results['distance_to_point']<=50:
                            ## final to result's Qitem
                            self.shap_data_store={
                                    "case_type": case_type,
                                    'case_kind':type_info['case_kind'],
                                    "score": -20,
                                    'items':[{
                                        'item':'鐵道',
                                        'item_name':shap_results['RAILNAME'],
                                        #'case_kind':'C',
                                        'radius':shap_results["distance_to_point"]}]
                                    }
                        else:
                            pass
                            
                    ## google map searched items--
                    # 使用字典來存儲唯一的地標，key 為 (place_id, feature_types) 組合
                    unique_landmarks = {}
                    for landmark in landmarks:
                        if 'place_id' in landmark:
                            # 使用 tuple 作為 key，因為它是不可變的
                            unique_key = (landmark['place_id'], landmark.get('feature_types', ''))
                            if unique_key not in unique_landmarks:
                                unique_landmarks[unique_key] = landmark

                    # 將唯一的地標轉換回列表
                    landmarks = list(unique_landmarks.values())

                    # 然後再進行距離檢查和其他處理
                    valid_landmarks = []  # 先收集所有有效的地標
                    landmark_cache = {}
                    
                    # 計算所有地標的距離
                    for landmark in landmarks:
                        if 'place_id' in landmark:
                            if landmark['place_id'] not in landmark_cache:
                                distance_result = google_places.calculate_distance_matrix(
                                    origin_lat=lat,
                                    origin_lng=lon,
                                    destination_id=landmark['destination']
                                )
                                if distance_result and distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                                    walking_distance = distance_result['rows'][0]['elements'][0]['distance']['value']
                                    landmark_cache[landmark['place_id']] = walking_distance
                                    landmark['radius'] = walking_distance
                            else:
                                landmark['radius'] = landmark_cache[landmark['place_id']]
                            
                            # 檢查距離是否在範圍內
                            if landmark.get('radius') and landmark['radius'] <= case['distance']:
                                valid_landmarks.append({
                                    'item': landmark.get('feature_types', ''),
                                    'item_name': landmark['name'],
                                    #'case_kind': landmark['case_kind'],
                                    'radius': landmark['radius']  # 統一使用 radius
                                })
                        else:
                             landmark['radius'] = landmark_cache[landmark['place_id']]
                        
                    if valid_landmarks:
                        valid_landmarks.sort(key=lambda x: x['radius'])

                    print("[DEBUG]-valid_landmarks:", valid_landmarks)
                    
                    # 去除重複的 feature_type，保留距離最近的
                    unique_valid_items = {}
                    
                    for landmark in valid_landmarks:
                        item = landmark['item']
                        if item not in unique_valid_items:
                            unique_valid_items[item] = landmark
                            print(f"[DEBUG] unique_valid_items:{unique_valid_items}")
                    
                    # 將唯一的有效地標加入結果
                    case_result['items']=list(unique_valid_items.values())
                    
                    ## case_result-> {'case_type': '004', 'case_kind': 'A', 'case_name': '以上小項皆無', 'score':0, 'items':[]}
                results['Qitem'].append(case_result)
            
            except Exception as e:
                print(f"Error processing {case_type}: {str(e)}")
                case_result['items']=[]
                results['Qitem'].append(case_result)
                
            print(f" [DEBUG] final_result-", results)
            ## 加上鐵路距離計算
            if self.shap_data_store:
                results['Qitem'].append(self.shap_data_store)

        
        ## 加入其他小項皆無的題目
        item1 = {'case_type': '004', 'case_kind': 'A', 'case_name': '以上小項皆無', 'score':0, 'items':[]}
        item2 = {'case_type': '010', 'case_kind': 'B', 'case_name': '以上小項皆無', 'score':0, 'items':[]}
        item3 = {'case_type': '022', 'case_kind': 'C', 'case_name': '以上小項皆無', 'score':0, 'items':[]}
        results['Qitem'].append(item1)
        results['Qitem'].append(item2)
        results['Qitem'].append(item3)

            # 如果有符合條件的地標，設置分數
        for record in results['Qitem']:
            if record['items']:
                case_type1 = record['case_type']
                # 從 Config.LANDMARK_SCORES 獲取分數
                form_scores = Config.LANDMARK_SCORES.get(form_type, {})  ## 表單型號 C或 D
                record['score'] = form_scores.get(case_type1, 0)
                print(f"Setting score for case_type {case_type1}: {record}")
            else:
                ## 否則是0分，預設是NULL
                record['score'] = 0
        results["Qitem"] = sorted(results["Qitem"], key=lambda x: int(x["case_type"]))
        
        return results
