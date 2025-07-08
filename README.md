# 🗺️ Research Agent — Nearby Landmark Search API  
研究型地標搜尋代理服務（REST API）

---

## 📌 What is this? | 這是什麼？

This project provides a **Research Agent** that exposes a **Flask RESTful API** for **automatic location-based landmark search & scoring**.

本專案提供一個基於 **Flask** 的 **RESTful API**，用於**自動化地標搜尋、距離計算及分數化**，  
適用於都市規劃、選址分析、風險評估等應用。

### 查詢
---

## 🚀 Key Features | 主要功能

✅ **Multi-source search | 多來源搜尋**  
- Google Places API：Nearby Search、Autocomplete  
- Local shapefiles（如鐵軌、行政界線等）

✅ **Distance Validation | 距離驗證**  
- Google Distance Matrix 計算真實步行距離

✅ **Config-driven Scoring | 規則化評分**  
- 搜尋類型、距離門檻、分數權重可依 `Config` 客製化

✅ **Async API | 非同步 API**  
- 後端使用背景執行緒，避免請求阻塞

✅ **Status Tracking | 查詢進度追蹤**  
- `/status/<request_id>` 取得執行結果


---

## 📡 How to Use API | API 使用方式

---

### 1️⃣ 發送查詢 | Submit a Search

```bash
POST /searchNearby
Content-Type: application/json

{
  "lat": 25.0330,
  "lon": 121.5654,
  "case_id": "ABC123",
  "form_type": "C"
}


# ✅ How it works | 背後執行邏輯

- Flask 先驗證請求參數
- 背景執行緒執行 `LandmarkSearch.search_landmarks()`：
  - Google Nearby Search & Autocomplete
  - Local shapefile 搜尋（如鐵軌）
  - 關鍵字過濾、類型篩選
  - Google Distance Matrix 計算真實距離
  - 套用 `Config` 設定的分數
- 結果以 `request_id` 暫存在記憶體，可透過 `/status` 查詢

---

## Config Highlights | Config 重點

- `LANDMARK_TYPES` ➜ 定義地標類別、搜尋半徑、搜尋來源  
- `LANDMARK_SCORES` ➜ 表單型號對應分數  
- `PLACE_TYPE_MAPPING` ➜ Google Places 類型對應內部 `case_type`

---

## Extend or Customize | 擴充調整

- 新增地標 ➜ 修改 `Config.LANDMARK_TYPES`
- 增加 shapefile ➜ 修改 `localLandmarkSearch.py`
- 調整分數 ➜ 更新 `Config.LANDMARK_SCORES`
- 改逾時 ➜ 修改 `timeout_manager.py`
- 需要 Docker ➜ 自行新增 `Dockerfile`

---

## ⚠️ Security Notice | 安全提醒

**此 Repo 為公開倉庫**  
**請勿提交真實 Google Maps API Key！**



