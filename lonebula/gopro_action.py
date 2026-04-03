import requests
import sys

BASE = "http://10.5.5.9:8080/gopro/camera"

def do_action(action):
    try:
        if action == "start":
            r = requests.get(f"{BASE}/shutter/start", timeout=3)
            print(f"[GoPro 3.11] 録画開始シグナル送信: {r.status_code}")
        elif action == "stop":
            r = requests.get(f"{BASE}/shutter/stop", timeout=3)
            print(f"[GoPro 3.11] 録画停止シグナル送信: {r.status_code}")
    except Exception as e:
        print(f"[GoPro 3.11] エラー発生: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        do_action(sys.argv[1])