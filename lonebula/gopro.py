# gopro_ssi.py
import requests
import time

BASE = "http://10.5.5.9:8080/gopro/camera"

# SSIにデータの次元数と型を伝える
def getSampleDimensionOut():
    return 1

def getSampleTypeOut():
    return 1 # FLOAT

def getSampleRateOut():
    return 1.0 # 1Hz (1秒に1回ステータスを取得)

def connect():
    """SSIのパイプライン開始時に呼ばれる（録画開始）"""
    try:
        requests.get(f"{BASE}/shutter/start", timeout=3)
        print("GoPro Recording Started")
    except Exception as e:
        print(f"Failed to start GoPro: {e}")

def disconnect():
    """SSIのパイプライン終了時に呼ばれる（録画停止）"""
    try:
        requests.get(f"{BASE}/shutter/stop", timeout=3)
        print("GoPro Recording Stopped")
    except Exception as e:
        print(f"Failed to stop GoPro: {e}")

def read(opts, vars, data):
    """SSI実行中に連続して呼ばれる（ステータス保存用）"""
    try:
        r = requests.get(f"{BASE}/state", timeout=3)
        # 接続成功状態として 1.0 をSSIに渡す（本来はJSONから特定の設定値を抽出して渡すことも可能）
        data[0] = 1.0
    except:
        # エラー時は 0.0
        data[0] = 0.0