from flask import Flask, request, jsonify
import threading
import time

# 假設這些工具放在 utils/ 裡，請自行調整路徑
from utils.request_handler import validate_request, format_response
from utils.timeout_manager import TimeoutManager

# LandmarkSearch 在 nearbySearch.py，並有 search_landmarks 函式
from nearbySearch import LandmarkSearch

app = Flask(__name__)

# 正在查詢的請求 (防止 300 秒內重複查詢)
on_going_requests = {}
# 查詢完成後的結果
search_results = {}

timeout_manager = TimeoutManager()
TIMEOUT_SECONDS = 300

def run_landmark_search(lat, lon, case_id, form_type, request_id):
    """
    在背景執行緒進行真正的查詢邏輯，並在 300 秒內未完成則視為失敗。
    """
    print(f"[DEBUG] 執行 LandmarkSearch, request_id={request_id}")
    start_time = time.time()
    try:
        # === 這裡是「查詢邏輯」 ===
        # 你可以直接呼叫 LandmarkSearch() 裡的函式
        # 假設它可能耗時，所以我們在下面檢查耗時
        output = LandmarkSearch().search_landmarks(lat, lon, case_id, form_type)
        
        print(f"[DEBUG] search_landmarks() 執行完成, output={output}")

        # 手動檢查一下時間，若超過 TIMEOUT_SECONDS，就視為失敗
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_SECONDS:
            search_results[request_id] = {
                "status": "error",
                "message": "時間過長，請重新查詢"
            }
        else:
            search_results[request_id] = {
                "status": "success",
                "data": output
            }

    except Exception as e:
        # 有錯誤 => 記錄結果
        print(f"[ERROR] LandmarkSearch 執行錯誤: {e}")
        search_results[request_id] = {
            "status": "error",
            "message": str(e)
        }
    finally:
        # 無論成功失敗，都從 on_going_requests 移除
        on_going_requests.pop(request_id, None)
        timeout_manager.remove_request(request_id)
        print(f"[DEBUG] 查詢結束, request_id={request_id}")

@app.route('/nearbysearch', methods=['POST'])
def nearby_search():
    """
    1) 驗證參數 -> 產生 request_id
    2) 檢查 300 秒內是否重複查詢
    3) 背景執行緒進行查詢
    4) 立即回傳 202 + request_id
    """
    data = request.get_json()
    print("[DEBUG] 收到的 JSON:", data)

    if not data:
        return jsonify(format_response("error", "未收到參數")), 400

    # 驗證參數 & 產生 request_id
    validation_result = validate_request(data)
    if validation_result["status"] == "error":
        return jsonify(format_response("error", validation_result["message"])), 403

    request_id = validation_result["request_id"]
    print("[DEBUG] request_id =", request_id)

    # 2. 檢查 300 秒內重複查詢
    if request_id in on_going_requests:
        # 表示還在處理中
        return jsonify(format_response("error", "已查詢中，短時間內勿再查詢")), 429

    # 如果先前查詢過，而且在 search_results 找到結果，表示查詢完成
    # 若你想完全禁止同參數多次查詢，也可在這裡回覆
    # 但若要允許重查，可以忽略這段
    if request_id in search_results:
        # 代表之前的查詢已經完成，若要重新查，應該用不同參數
        return jsonify(format_response("error", "該參數查詢結果已存在，請使用不同參數")), 409

    # 解析參數
    lat = data["lat"]
    lon = data["lon"]
    case_id = data["case_id"]
    form_type = data["form_type"]

    # 記錄這個請求正在處理
    on_going_requests[request_id] = True
    timeout_manager.add_request(request_id, TIMEOUT_SECONDS)

    # 背景執行緒執行 run_landmark_search
    thread = threading.Thread(
        target=run_landmark_search,
        args=(lat, lon, case_id, form_type, request_id),
        daemon=True  # daemon=True 表示主程式結束時會關掉
    )
    thread.start()

    # 先回傳 202 + request_id
    return jsonify({
        "status": "received",
        "message": "已收到查詢請求，請稍候",
        "request_id": request_id
    }), 202

@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    """
    客戶端自行輪詢 /status/<request_id> 取得最終結果或目前狀態
    """
    print(f"[DEBUG] /status/{request_id}")

    # 還在處理中
    if request_id in on_going_requests:
        return jsonify({
            "status": "processing",
            "message": "查詢中，請稍候"
        }), 200

    # 已查詢完成 (成功或失敗) => 取出結果
    if request_id in search_results:
        return jsonify(search_results[request_id]), 200

    # 都沒有 => 查無此 request_id (可能超時被清掉或請求不合法)
    return jsonify({
        "status": "error",
        "message": "找不到對應的查詢結果"
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
