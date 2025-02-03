from flask import Flask, request, jsonify
import threading
import time

# 假設這些工具放在 utils/ 內，請自行調整路徑
from utils.request_handler import validate_request, format_response
from utils.timeout_manager import TimeoutManager

# 假設 LandmarkSearch 放在 nearbySearch.py，並有一個 search_landmarks 函式
from nearbySearch import LandmarkSearch  

app = Flask(__name__)

# 正在查詢中的請求 (防止重複查詢)
on_going_requests = {}
# 查詢完成後的結果暫存在這裡
search_results = {}

timeout_manager = TimeoutManager()
TIMEOUT_SECONDS = 300

def run_landmark_search(lat, lon, case_id, form_type, request_id):
    """
    背景執行緒：真正執行 LandmarkSearch 的邏輯
    """
    print(f"[DEBUG] 執行 LandmarkSearch, request_id={request_id}")
    try:
        # 呼叫你的 LandmarkSearch 查詢 (可能耗時)
        output = LandmarkSearch().search_landmarks(lat, lon, case_id, form_type)
        # 查詢完成，存入 search_results
        search_results[request_id] = {
            "status": "success",
            "data": output
        }
    except Exception as e:
        # 有錯誤也要寫入結果
        search_results[request_id] = {
            "status": "error",
            "message": str(e)
        }
    finally:
        # 移除正在查詢中的請求
        on_going_requests.pop(request_id, None)
        timeout_manager.remove_request(request_id)

@app.route('/searchNearby', methods=['POST'])
def nearby_search():
    """
    1) 收到查詢參數
    2) 驗證 + 生成 request_id
    3) 若無重複查詢，就透過執行緒呼叫 run_landmark_search
    4) 立即回傳 202 + request_id
    """
    data = request.get_json()
    print("[DEBUG] 收到的 JSON:", data)

    if not data:
        return jsonify(format_response("error", "未收到參數")), 400

    # 驗證請求參數
    validation_result = validate_request(data)
    if validation_result["status"] == "error":
        return jsonify(format_response("error", validation_result["message"])), 400

    request_id = validation_result["request_id"]
    print("[DEBUG] request_id =", request_id)

    # 檢查是否重複查詢
    if request_id in on_going_requests:
        return jsonify(format_response("error", "重複查詢，請稍候再試")), 429

    # 檢查是否已有結果 (代表之前同參數已經查詢過)
    if request_id in search_results:
        return jsonify({
            "status": "success",
            "message": "之前已查詢完成，可直接取得結果",
            "request_id": request_id
        }), 200

    # 解析參數
    lat = data["lat"]
    lon = data["lon"]
    case_id = data["case_id"]
    form_type = data["form_type"]

    # 記錄該請求正在處理
    on_going_requests[request_id] = True
    timeout_manager.add_request(request_id, TIMEOUT_SECONDS)

    # 使用 Thread 執行 LandmarkSearch
    thread = threading.Thread(target=run_landmark_search, args=(lat, lon, case_id, form_type, request_id))
    thread.start()

    # 立刻回傳 202 (Accepted) + request_id
    return jsonify({
        "status": "received",
        "message": "已收到查詢請求，請稍候",
        "request_id": request_id
    }), 202

@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    """
    用戶端自行輪詢或查詢此路由，取得最終結果或目前狀態
    """
    print(f"[DEBUG] 查詢 status, request_id={request_id}")

    # 如果還在執行中
    if request_id in on_going_requests:
        return jsonify({
            "status": "processing",
            "message": "查詢中，請稍候"
        }), 200

    # 如果已查完 (或失敗)，結果存在 search_results
    if request_id in search_results:
        return jsonify(search_results[request_id]), 200

    # 都沒有 => 找不到此 request_id，可能超時或不正確
    return jsonify({
        "status": "error",
        "message": "找不到對應的查詢結果"
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
