import sys
import time
from unittest.mock import MagicMock

# pynputのエラー回避
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from xdpchandler import *

def main():
    print("Initializing Xsens DOT SDK in 'movella' environment...")
    handler = XdpcHandler()
    if not handler.initialize():
        print("Failed to initialize XdpcHandler")
        return
        
    handler.scanForDots()
    if len(handler.detectedDots()) == 0:
        print("No DOTs detected")
        return
        
    handler.connectDots()
    connected = handler.connectedDots()
    if not connected:
        print("Failed to connect to DOTs")
        return

    print(f"Connected to {len(connected)} DOTs. Starting measurement...")
    for device in connected:
        device.setOutputRate(60)
        device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion)

    target_mac = connected[0].bluetoothAddress()
    print(f"Targeting DOT with MAC: {target_mac}")
    
    count = 0
    try:
        while True:
            if handler.packetsAvailable():
                # 【重要】全デバイスのパケットを回収してバッファの渋滞を防ぐ
                for device in connected:
                    m = device.bluetoothAddress()
                    p = handler.getNextPacket(m)
                    
                    # 対象の1台目 (target_mac) のデータだけをSSIへ送信
                    if m == target_mac and p:
                        if p.containsOrientation() and p.containsFreeAcceleration():
                            time_fine = p.sampleTimeFine()
                            quat = p.orientationQuaternion()
                            acc = p.freeAcceleration()
                            status = p.status()
                            
                            print(f"{time_fine},{quat[0]},{quat[1]},{quat[2]},{quat[3]},{acc[0]},{acc[1]},{acc[2]},{status}", flush=True)
                            
                            # デバッグ用：約5秒(300フレーム)に1回、生存報告を出す
                            count += 1
                            if count % 300 == 0:
                                print(f"DEBUG: Successfully streaming data. time={time_fine}")
            else:
                time.sleep(0.001)
                
    except KeyboardInterrupt:
        print("Stopping measurement...")
    finally:
        for device in connected:
            device.stopMeasurement()
        handler.cleanup()

if __name__ == "__main__":
    main()