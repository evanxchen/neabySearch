import requests
import json
import os
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from config import Config
import numpy as np 
import numpy as np
from scipy.spatial import KDTree
import geopandas as gpd
from shapely.geometry import Point
os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# 載入環境變數
# load_dotenv('config.env')

# 載入環境變數
load_dotenv('config.env')

class GooglePlacesAPI:
    """Google Places API 操作類"""
    
    def __init__(self, api_key: str = None):
        """初始化 Google Places API 客戶端"""
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set it in config.env or pass it to the constructor.")
            
        self.api_key_header = {
            "X-Goog-Api-Key": self.api_key
        }

    def _create_location_restriction(self, latitude: float, longitude: float, radius: float) -> Dict:
        """
        創建位置限制參數
        
        Args:
            latitude: 緯度
            longitude: 經度
            radius: 搜尋半徑（米）
        """
        return {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius
            }
        }
        
    def autocomplete_search(self, input_text: str, latitude: float, longitude: float, radius: float, 
                          included_types: list = None) -> Optional[Dict]:
        """
        使用 Google Places Autocomplete API 搜尋地標
        
        Args:
            input_text: 搜尋關鍵字
            latitude: 緯度
            longitude: 經度
            radius: 搜尋半徑（米）
            included_types: 包含的地標類型列表
        """
        url = "https://places.googleapis.com/v1/places:autocomplete"
        
        search_params = {
            "input": input_text,  
            "locationRestriction": {  # 改用 locationBias
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius  # 確保 radius 是浮點數
                }
            },
            "languageCode": "zh-TW",
            "regionCode":"tw"
        }
        
        if included_types:
            search_params["includedPrimaryTypes"] = included_types
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }
        
        try:
            response = requests.post(url, json=search_params, headers=headers)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Autocomplete search error: {str(e)}")
            return None

    def nearby_search(self, latitude: float, longitude: float, radius: float,
                     included_types: list = None, includedPrimaryTypes:list=None, excludedPrimaryTypes:list=None, max_results: int = 1) -> Optional[Dict]:
        """
        使用 Google Places Nearby Search API 搜尋地標
        
        Args:
            latitude: 緯度
            longitude: 經度
            radius: 搜尋半徑（米）
            included_types: 包含的地標類型列表
            max_results: 最大結果數量
        """
        url = "https://places.googleapis.com/v1/places:searchNearby"
        
        search_params = {
            "languageCode": "zh-TW",
            "maxResultCount": max_results,
            "locationRestriction": self._create_location_restriction(latitude, longitude, radius),
            "rankPreference": "distance"
        }
        
        if included_types:
            search_params["includedTypes"] = included_types
        
        if includedPrimaryTypes:
            search_params['includedPrimaryTypes']=includedPrimaryTypes
        
        if excludedPrimaryTypes:
            search_params['excludedPrimaryTypes']=excludedPrimaryTypes
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            **self.api_key_header,
            "X-Goog-FieldMask": "places"
        }
        
        try:
            response = requests.post(url, json=search_params, headers=headers)
            response.raise_for_status()
            #print(response.status_code)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Nearby search error: {str(e)}")
            return None
    

    def calculate_distance_matrix(self, origin_lat: float, origin_lng: float, dest_lat:float=None, dest_lon:float =None,destination_id: str=None) -> Optional[Dict]:
        """
        使用 Google Distance Matrix API 計算兩點間的步行距離
        
        Args:
            origin_lat: 起點緯度
            origin_lng: 起點經度
            destination_id: 終點的 place_id
        """
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        if destination_id:
            params = {
                "origins": f"{origin_lat},{origin_lng}",
                "destinations": destination_id,
                "mode": "walking",
                "language": "zh-TW",
                "key": self.api_key
            }
        else :
            params = {
                "origins": f"{origin_lat},{origin_lng}",
                "destinations": f"{dest_lat},{dest_lon}",
                "mode": "walking",
                "language": "zh-TW",
                "key": self.api_key
            }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Distance matrix calculation error: {str(e)}")
            return None

    def check_address_descriptor(self, place: Dict, config: object) -> list:
        """
        檢查 addressDescriptor 中的地標是否符合搜尋類型
        """
        landmarks_result = []
        try:
            if len(place.get('addressDescriptor')) > 0:
                landmark = place['addressDescriptor']
                landmark_types = landmark.get('landmarks')
                    # 遍歷所有 landmarks
            for landmark_items in landmark_types:
                for category_id, category_info in Config.PLACE_TYPE_MAPPING.items():
                    for type_combination in category_info:
                            for type_combinations in type_combination['check_types']:
                                if type_combinations==landmark_items['types']:
                                    landmarks_result.append({
                                        'case_type': category_id,
                                        'case_kind': type_combination['case_kind'],
                                        'place_id': landmark_items['placeId'],
                                        'name': landmark_items['displayName']['text'],
                                        'distance': None,
                                        'features_types': type_combination['case_type']
                                    })
        except Exception as e:
            print(f"Error processing addressDescriptor: {str(e)}")
        return landmarks_result