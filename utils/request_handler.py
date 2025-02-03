import re

def validate_request(data):
    """
    驗證請求參數是否符合規範：
    - lat: 必須是 21~27 之間的 float
    - lon: 必須是 120~123 之間的 float
    - case_id: 至少 8 碼
    - form_type: 只能是 "A" 或 "B"
    """
    
    # 確保所有必要參數都存在
    required_keys = ["lat", "lon", "case_id", "form_type"]
    for key in required_keys:
        if key not in data:
            return {"status": "error", "message": f"缺少必要參數: {key}"}

    lat = data.get("lat")
    lon = data.get("lon")
    case_id = data.get("case_id")
    form_type = data.get("form_type")

    # 檢查 lat 是否在 21-27 之間
    if not isinstance(lat, (int, float)) or not (22 <= lat <= 26):
        return {"status": "error", "message": "lat 參數必須是 21~27 之間的浮點數"}

    # 檢查 lon 是否在 120-123 之間
    if not isinstance(lon, (int, float)) or not (120 <= lon <= 122):
        return {"status": "error", "message": "lon 參數必須是 120~123 之間的浮點數"}

    # 檢查 case_id 是否至少 11 碼
    if not isinstance(case_id, str) or not re.match(r"^\d{11,}$", case_id):
        return {"status": "error", "message": "case_id 參數必須是至少 11 碼的數字字串"}

    # 檢查 form_type 是否為 "A" 或 "B"
    if form_type not in ["A", "B"]:
        return {"status": "error", "message": "form_type 參數必須是 'A' 或 'B'"}

    # 產生 request_id 作為查詢的唯一標識
    request_id = f"{lat}_{lon}_{case_id}_{form_type}"
    return {"status": "success", "request_id": request_id}

def format_response(status, message):
    """
    統一 API 回傳格式
    """
    return {"status": status, "message": message}