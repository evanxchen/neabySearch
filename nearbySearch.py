import requests
import json
import os
from typing import Dict, Optional, Tuple
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
            'CASE_ID': case_id,
            'Form_type': form_type,
            'LAT': lat,
            'LON': lon,
            'Qitem': []
        }
        ## 遍歷LANDMARK_TYPES
        for case_type, type_info in Config.LANDMARK_TYPES.items():
            case_result = {
                'case_type': case_type,
                'case_kind': type_info['case_kind'],
                'case_name': type_info['name'],
                'score': None,
                'item': []
            }
            try:
                valid_landmarks = []
                landmarks=[]
                #local_landmarks=[]
                # 遍歷每個 case
                for case in type_info['cases']:
                    #print(f"[DEBUG] case_type: {case_type}, case: {case}")
                    
                    search_method_type = case['search_methods']['type']
                    found_in_nearby = False
                    
                    # 處理 nearby 搜尋
                    if (search_method_type=='nearby_only' or search_method_type =='nearby_first'):
                        if 'nearby' in case['search_methods']:
                            nearby_params = case['search_methods']['nearby']['params']
                            nearby_results = google_places.nearby_search(
                                latitude=lat,
                                longitude=lon,
                                radius=case['distance'],
                                included_types=nearby_params['includedTypes'],
                                max_results=nearby_params['maxResultCount']
                            )
                            
                            #print("[DEBUG] nearby_search() 回傳:", nearby_results)
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
                                    'item':[{
                                        'item':'鐵道',
                                        'item_name':shap_results['RAILNAME'],
                                        'case_kind':'C',
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
                                    'case_kind': landmark['case_kind'],
                                    'radius': landmark['radius']  # 統一使用 radius
                                })
                        else:
                             landmark['radius'] = landmark_cache[landmark['place_id']]
                        
                    if valid_landmarks:
                        valid_landmarks.sort(key=lambda x: x['radius'])
                    
                    # 去除重複的 feature_type，保留距離最近的
                    unique_valid_items = {}
                    for landmark in valid_landmarks:
                        item = landmark['item']
                        if item not in unique_valid_items:
                            unique_valid_items[item] = landmark
                    
                    # 將唯一的有效地標加入結果
                    case_result['item'] = list(unique_valid_items.values())
            
                     # 如果有符合條件的地標，設置分數
                    if case_result['item']:
                        # 從 Config.LANDMARK_SCORES 獲取分數
                        form_scores = Config.LANDMARK_SCORES.get(form_type, {})
                        case_result['score'] = form_scores.get(case_type, 0)
                        print(f"Setting score for case_type {case_type}: {case_result['score']}")
                    else:
                        ## 否則是0分，預設是NULL
                        case_result['score'] = 0
                        
            except Exception as e:
                        print(f"Error processing {case_type}: {str(e)}")
                        case_result['score'] = 0

            results['Qitem'].append(case_result)
            
            
        
            ## 加上鐵路距離計算
            if self.shap_data_store:
                results['Qitem'].append(self.shap_data_store)
                
            ## 加入其他小項皆無的題目
        item1 = {'case_type': '004', 'case_kind': 'A', 'case_name': '以上小項皆無', 'score':0, 'item':[]}
        item2 = {'case_type': '010', 'case_kind': 'B', 'case_name': '以上小項皆無', 'score':0, 'item':[]}
        item3 = {'case_type': '022', 'case_kind': 'C', 'case_name': '以上小項皆無', 'score':0, 'item':[]}
        results['Qitem'].append(item1)
        results['Qitem'].append(item2)
        results['Qitem'].append(item3)
        results["Qitem"] = sorted(results["Qitem"], key=lambda x: int(x["case_type"]))   
            #print("[DEBUG] 最終回傳的 results:", results)
            
        return results