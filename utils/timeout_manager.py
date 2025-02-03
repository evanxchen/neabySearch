import threading

class TimeoutManager:
    """
    用於管理請求超時的工具類。
    """
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()

    def add_request(self, request_id, timeout):
        """
        添加請求並設定超時計時器。
        """
        with self.lock:
            if request_id in self.requests:
                return
            
            timer = threading.Timer(timeout, self.remove_request, args=[request_id])
            self.requests[request_id] = timer
            timer.start()

    def remove_request(self, request_id):
        """
        移除已超時或已完成的請求。
        """
        with self.lock:
            if request_id in self.requests:
                self.requests[request_id].cancel()
                del self.requests[request_id]
