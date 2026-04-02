import threading
import asyncio
import queue
import numpy as np
from open_gopro import WirelessGoPro

class GoProSensor:
    def __init__(self, **kwargs):
        # SSIからの設定引数
        self.sr = float(kwargs.get('sr', 10.0))  # サンプリングレート
        self.data_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None
        self.gopro = None

    def connect(self):
        """SSI起動時に呼ばれる初期化処理"""
        self.thread = threading.Thread(target=self._run_gopro_loop, daemon=True)
        self.thread.start()

    def _run_gopro_loop(self):
        """別スレッドでGoProの非同期通信を回す"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._gopro_async_task())

    async def _gopro_async_task(self):
        async with WirelessGoPro() as gopro:
            self.gopro = gopro
            # 接続確認
            print("Successfully connected to GoPro!")
            
            while not self.stop_event.is_set():
                # 例としてバッテリーレベルを取得（実際はIMUなども可能）
                # 取得頻度は sr (10Hz) に合わせる
                result = await gopro.ble_setting.resolution.get_value()
                val = float(result.flatten) if result.is_ok else 0.0
                
                self.data_queue.put(val)
                await asyncio.sleep(1.0 / self.sr)

    def read(self, data):
        """SSIのメインループから呼ばれるデータ取得（同期）"""
        for i in range(len(data)):
            try:
                # キューから最新データを取り出す。なければ最後の値を保持
                data[i] = self.data_queue.get_nowait()
            except queue.Empty:
                data[i] = 0.0 if i == 0 else data[i-1]

    def disconnect(self):
        """SSI終了時に呼ばれるクリーンアップ"""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)