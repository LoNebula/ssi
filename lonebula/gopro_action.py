import requests
import sys

BASE = "http://10.5.5.9:8080/gopro/camera"

def do_action(action):
    try:
        if action == "start":
            r = requests.get(f"{BASE}/shutter/start", timeout=3)
            print(f"[GoPro] 録画開始: {r.status_code}")
        elif action == "stop":
            r = requests.get(f"{BASE}/shutter/stop", timeout=3)
            print(f"[GoPro] 録画停止: {r.status_code}")
        elif action == "stream_start":
            # UDP 8554ポートへのプレビュー映像配信を開始
            r = requests.get(f"{BASE}/stream/start", timeout=3)
            print(f"[GoPro] ストリーム開始: {r.status_code}")
        elif action == "stream_stop":
            # プレビュー映像配信を停止
            r = requests.get(f"{BASE}/stream/stop", timeout=3)
            print(f"[GoPro] ストリーム停止: {r.status_code}")
    except Exception as e:
        print(f"[GoPro] エラー: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        do_action(sys.argv[1])