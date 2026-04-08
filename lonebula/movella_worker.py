import sys
import os
import time
import glob
from unittest.mock import MagicMock

sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from xdpchandler import *

# SSIの画面と.streamに同期させるメインの1台のMACアドレスを固定
TARGET_MAC = "D4:22:CD:07:AA:B5"

def main():
    xdpcHandler = XdpcHandler()
    if not xdpcHandler.initialize():
        print("[Movella Worker] Failed to initialize handler", flush=True)
        return
        
    xdpcHandler.scanForDots()
    if len(xdpcHandler.detectedDots()) == 0:
        print("[Movella Worker] No Movella DOT device(s) found.", flush=True)
        return
        
    print("[Movella Worker] Connecting to dots...", flush=True)
    xdpcHandler.connectDots()
    connected = xdpcHandler.connectedDots()
    
    if not connected:
        print("[Movella Worker] Could not connect to any dots.", flush=True)
        return

    print(f"[Movella Worker] Connected to {len(connected)} devices.", flush=True)

    # SSIがたった今作成した最新の「data/日付」フォルダを自動取得
    out_dir = "."
    dirs = glob.glob("data/*/")
    if dirs:
        out_dir = max(dirs, key=os.path.getctime)
        
    for device in connected:
        device.setOutputRate(60)
        mac = device.portInfo().bluetoothAddress()
        
        # Filter Profileを明示的にセットする (必須)
        device.setOnboardFilterProfile("General")
        
        # 5台すべての生データを最新フォルダ内に保存
        device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
        filename = os.path.join(out_dir, f"logfile_{mac.replace(':', '-')}.csv")
        device.enableLogging(filename)
        
        # 計測開始
        device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion)

    debug_drop_count = 0

    try:
        while True:
            if xdpcHandler.packetsAvailable():
                for device in connected:
                    mac = device.portInfo().bluetoothAddress()
                    packet = xdpcHandler.getNextPacket(mac)
                    
                    if mac == TARGET_MAC:
                        if packet is not None and packet.containsOrientation():
                            try:
                                time_fine = packet.sampleTimeFine() if hasattr(packet, 'sampleTimeFine') else 0
                                
                                # クォータニオンの取得 (NumPy配列 / オブジェクト両対応)
                                quat = packet.orientationQuaternion()
                                if hasattr(quat, 'w'): # オブジェクトの場合
                                    qw, qx, qy, qz = quat.w(), quat.x(), quat.y(), quat.z()
                                else: # NumPy配列やリストの場合
                                    qw, qx, qy, qz = quat[0], quat[1], quat[2], quat[3]

                                # 加速度の取得 (NumPy配列 / オブジェクト両対応)
                                ax, ay, az = 0.0, 0.0, 0.0
                                if packet.containsFreeAcceleration():
                                    acc = packet.freeAcceleration()
                                    if hasattr(acc, 'x'):
                                        ax, ay, az = acc.x(), acc.y(), acc.z()
                                    else:
                                        ax, ay, az = acc[0], acc[1], acc[2]
                                        
                                status = packet.status() if hasattr(packet, 'status') else 0
                                
                                # SSIに9次元データを送る
                                print(f"{time_fine},{qw},{qx},{qy},{qz},{ax},{ay},{az},{status}", flush=True)
                                debug_drop_count = 0  
                                
                            except Exception as e:
                                print(f"[Movella Worker] Parsing Error: {e}", flush=True)
                        else:
                            debug_drop_count += 1
                            if debug_drop_count % 300 == 0:
                                print(f"[Movella Worker] WARNING: No Orientation data arriving for TARGET_MAC.", flush=True)
            else:
                time.sleep(0.001)
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[Movella Worker] FATAL: {e}", flush=True)
    finally:
        for device in connected:
            device.stopMeasurement()
            device.disableLogging()
        xdpcHandler.cleanup()

if __name__ == "__main__":
    main()