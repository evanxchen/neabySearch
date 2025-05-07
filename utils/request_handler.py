import re

def validate_request(data):
    """
    驗證請求參數是否符合規範：
    - lat: 必須是 21~27 之間的 float
    - lon: 必須是 120~123 之間的 float
    - case_id: 須符合 {CD]094-113-001-01的規律
    - form_type: 只能是 "C" 或 "D"
    """
    
    # 確保所有必要參數都存在
    required_keys = ["LAT", "LON", "CASE_ID", "Form_Type"]
    for key in required_keys:
        if key not in data:
            return {"status": "error", "message": f"缺少必要參數: {key}"}

    lat = data.get("LAT")
    lon = data.get("LON")
    case_id = data.get("CASE_ID")
    form_type = data.get("Form_Type")

    # 檢查 lat 是否在 21-27 之間
    if not isinstance(lat, (int, float)) or not (22 <= lat <= 26):
        return {"status": "error", "message": "lat 參數必須是 21~27 之間的浮點數"}

    # 檢查 lon 是否在 120-123 之間
    if not isinstance(lon, (int, float)) or not (120 <= lon <= 122):
        return {"status": "error", "message": "lon 參數必須是 120~123 之間的浮點數"}

    # 檢查 case_id 是否至少 11 碼
    if not isinstance(case_id, str) or not re.match(r"^[CD]\d{3}-\d{3}-[0-9A-Z]{2}-\d{3}$", case_id):
        return {"status": "error", "message": "case_id 參數必須符合{CD]094-113-01-001的規律"}

    # 檢查 form_type 是否為 "C" 或 "D"
    if form_type not in ["C", "D"]:
        return {"status": "error", "message": "form_type 參數必須是 'C' 或 'D'"}

    # 產生 request_id 作為查詢的唯一標識
    request_id = f"{lat}_{lon}_{case_id}_{form_type}"
    return {"status": "success", "request_id": request_id}

def format_response(status, message):
    """
    統一 API 回傳格式
    """
    return {"status": status, "message": message}
