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


class LocalLandmarkSearch:
    """處理本地地標搜索的類"""
    
    def __init__(self, landmark_path=None):
        """初始化本地地標搜索"""
        if landmark_path is None:
            current_dir = os.path.dirname(__file__)
            landmark_path = os.path.join(current_dir, 'landmark_list.txt')
            
        self.landmark_file_path = landmark_path
        
        print("DEBUG: in __init__, self.__dict__:", self.__dict__)
        
        self.local_landmarks = self.load_local_landmarks()
        self.kdtree = None
        self.landmark_coords = None
        self.build_kdtree()
    
    def load_local_landmarks(self):
        """載入本地地標清單"""
        landmarks = []
        try:
            with open(self.landmark_file_path, 'r', encoding='utf-8') as f:
                # 跳過標題行
                next(f)
                for line in f:
                    name, lat, lon, subtype, desc = line.strip().split(',')
                    landmarks.append({
                        'name': name,
                        'latitude': float(lat),
                        'longitude': float(lon),
                        'subtype': subtype,
                        'description': desc
                    })
        except Exception as e:
            print(f"Error loading landmarks: {str(e)}")
        return landmarks
    
    def build_kdtree(self):
        """建立 KDTree 用於快速空間搜索"""
        try:
            if not self.local_landmarks:
                self.kdtree = None
                self.landmark_coords = None
                return
                
            # 將地標座標轉換為 numpy array
            self.landmark_coords = np.array([[lm['latitude'], lm['longitude']] 
                                           for lm in self.local_landmarks])
            # 建立 KDTree
            self.kdtree = KDTree(self.landmark_coords)
        except Exception as e:
            print(f"Error building KDTree: {str(e)}")
            self.kdtree = None
            self.landmark_coords = None
    
    def find_nearby_landmarks(self, lat, lon, radius_km, target_case_type=None):
        if not self.kdtree:
            return []
        """
        搜索指定範圍內的本地地標
        
        Args:
            lat (float): 查詢點的緯度
            lon (float): 查詢點的經度
            radius_km (float): 搜索半徑（公里）
            case_type (str): 主類型（例如："009"）
            target_case_type (str): 要搜索的具體類型（例如："紀念堂"）
        """
       
        
        # 將公里轉換為度數（1度約等於111公里）
        radius_deg = radius_km / 111.0
        query_point = np.array([lat, lon])
        
        # 使用 KDTree 找出範圍內的點
        indices = self.kdtree.query_ball_point(query_point, radius_deg)
        
        nearby_landmarks = []
        for idx in indices:
            landmark = self.local_landmarks[idx]
            
             # 直接匹配地標的類型與目標類型
            if target_case_type and landmark['subtype'] == target_case_type:
                nearby_landmarks.append({
                    'place_id': f"local_{idx}",
                    'name': landmark['name'],
                    'feature_types': target_case_type,
                    'latitude': landmark['latitude'],
                    'longitude': landmark['longitude'],
                    'subtype': landmark['subtype'],
                    'description': landmark['description'],
                    'source': 'local'  # 添加來源標記
                })
        return nearby_landmarks
    
    
    def find_point_by_shap(self, latitude, longitude):
        # 讀取 .shp 文件
        current_dir = os.path.dirname(__file__)
        # 和 Shapefile 的主檔名組合
        shp_file = os.path.join(current_dir, "RAIL_1121102.shp")
        
        rails = gpd.read_file(shp_file)
        # 確保坐標系統為 WGS84（EPSG:4326），否則轉換
        if rails.crs != "EPSG:4326":
            rails = rails.to_crs("EPSG:4326")
        rails = rails.to_crs("EPSG:3857")
        #24.916408331454836, 121.14610848603607
        # latitude = 24.916408331454836  # 替換為你的緯度
        # longitude = 121.14610848603607 # 替換為你的經度
        point = Point(longitude, latitude)  # 注意順序是 (經度, 緯度)
        point = gpd.GeoSeries([point], crs="EPSG:4326").to_crs("EPSG:3857").iloc[0]
        rails['distance_to_point'] = rails.geometry.apply(lambda line: line.distance(point))

        # 找到距離最短的 LINESTRING
        nearest_rail = rails.loc[rails['distance_to_point'].idxmin()]
        return nearest_rail
