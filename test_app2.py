from flask import Flask, request, jsonify
import threading
import time
import json
import requests
from utils.request_handler import validate_request, format_response
from utils.timeout_manager import TimeoutManager
from nearbySearch import LandmarkSearch

app = Flask(__name__)

# 正在查詢的請求 (防止 300 秒內重複查詢)
on_going_requests = {}
# 查詢完成後的結果
search_results = {}

timeout_manager = TimeoutManager()
TIMEOUT_SECONDS = 300


def access_token():
    url = 'https://10.14.88.77:9444/api/rest/app/verification'
    data = {"appId":"MLOPS", "appKey":"fcb123456"}
    response = requests.post(url, json=data, verify=False)
    if response.status_code==200:
        return response.json()['token']
    else: 
        return 'none'

def run_landmark_search(lat, lon, case_id, form_type, request_id):
    """
    背景執行緒：執行 LandmarkSearch 查詢，並在完成後自動呼叫客戶 API 傳送結果
    """
    print(f"[DEBUG] 執行 LandmarkSearch, request_id={request_id}")
    start_time = time.time()
    try:
        ## 正常結果
        output = LandmarkSearch().search_landmarks(lat, lon, case_id, form_type)
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_SECONDS:
            timeout_results = {
            "token": access_token(),
            "case_id":case_id,
            "LAT":lat,
            "LON":lon,
            "form_type": form_type,
            "returnCode":"0002",
            "returnMessage":"Timeout"
        }
            output = timeout_results
            search_results[request_id] = output
            print(f"[DEBUG] search_landmarks() 查詢超時, output={output}")    
        else:
            output["token"] = access_token()
            output.update(
                {"returnCode":"0000",
                "returnMessage":"Success"}
            )
            search_results[request_id] = output
            print(f"[DEBUG] search_landmarks() 執行完成, output={output}")
            
    except Exception as e:
        error_results = {
            "token": access_token(),
            "case_id":case_id,
            "LAT":lat,
            "LON":lon,
            "form_type": form_type,
            "returnCode":"0003",
            "returnMessage":"Failed"
        }
        #output = error_results
        search_results[request_id] = error_results
        print(f"[DEBUG] search_landmarks() 查詢失敗, output={error_results}")
        
    finally:
        ## 查詢中的參數移除結果
        on_going_requests.pop(request_id, None)
        timeout_manager.remove_request(request_id)
        print(f"[DEBUG] 查詢結束, request_id={request_id}")
        #call_customer_api(output)
        # try:
        #     with open ('target_testing_txt', "a", encoding='utf-8') as f:
        #         json.dump(results, f, ensure_ascii=False)
        #         f.write("\n")
        # except Exception as file_err:
        #     print(f"[ERROR] 寫入檔案錯誤:{file_err}")
        
        # ## 定時清理dict
        # if request_id in search_results:
        #     del search_results[request_id]

def clear_results(interval=1800):
    while True:
        time.sleep(interval)
        search_results.clear(1800)   ## 30分鐘清理
        print("[DEBUG] 定時清空 search results dictionary")

@app.route('/searchNearby', methods=['POST'])
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
    if request_id in search_results:
        # 代表之前的查詢已經完成，若要重新查，應該用不同參數
        return jsonify(format_response("error", "該參數查詢結果已存在，請使用不同參數")), 409

    # 解析參數
    lat = data["LAT"]
    lon = data["LON"]
    case_id = data["CASE_ID"]
    form_type = data["Form_Type"]

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

    # 都沒有 => 查無此 request_id
    return jsonify({
        "status": "error",
        "message": "找不到對應的查詢結果"
    }), 404


## 每60分鐘清空search_results
#threading.Thread(target=clear_results, args=(3600,), daemon =True).start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
