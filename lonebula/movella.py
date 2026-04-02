import sys
import time
from unittest.mock import MagicMock

# SSI環境（コンソールがない環境）でエラーになる pynput をダミー化
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from xdpchandler import *

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    # SSIの要求通り、値に文字列（説明文）を入れた辞書を返します
    return { 'sensor' : 'Movella DOT Orientation (Euler)' }

def initChannel(name, channel, types, opts, vars):
    # 元のコードに合わせて 60Hz, 3次元(FLOAT) に設定
    if name == 'sensor':
        channel.dim = 3
        channel.type = types.FLOAT
        channel.sr = 60.0

def connect(opts, vars):
    # movelladot_pc_sdk_receive_data.py の接続ロジック
    handler = XdpcHandler()
    if not handler.initialize():
        return False

    handler.scanForDots()
    if len(handler.detectedDots()) == 0:
        return False

    handler.connectDots()
    connected = handler.connectedDots()
    if not connected:
        return False

    # 接続した全デバイスに対して設定（元のコードに準拠）
    for device in connected:
        device.setOutputRate(60)
        device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
        device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler)

    # 後の関数で使う変数を保持
    vars['handler'] = handler
    vars['connected'] = connected
    vars['start_time'] = time.time()
    vars['reset_done'] = False
    
    # 1台目のMACアドレスを取得（read用）
    vars['mac'] = connected[0].bluetoothAddress()
    print(f"Connected to: {vars['mac']}")

def read(name, sout, reset, board, opts, vars):
    handler = vars['handler']
    mac = vars['mac']
    connected = vars['connected']
    
    # 元のコードにある「5秒後のHeading Reset」ロジック
    if not vars['reset_done'] and (time.time() - vars['start_time'] > 5.0):
        for device in connected:
            device.resetOrientation(movelladot_pc_sdk.XRM_Heading)
        print("\nOrientation Reset (Heading) Done.")
        vars['reset_done'] = True

    # 指定サンプル数分データを取得
    for i in range(sout.num):
        packet = None
        while packet is None:
            if handler.packetsAvailable():
                packet = handler.getNextPacket(mac)
                if not packet.containsOrientation():
                    packet = None
            else:
                time.sleep(0.001)
        
        # Euler角 (Roll, Pitch, Yaw)
        euler = packet.orientationEuler()
        sout[i, 0] = euler.x()
        sout[i, 1] = euler.y()
        sout[i, 2] = euler.z()

def disconnect(opts, vars):
    # 元のコードの終了ロジック（DefaultAlignmentへのリセットと停止）
    if 'connected' in vars:
        for device in vars['connected']:
            device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment)
            device.stopMeasurement()
    if 'handler' in vars:
        vars['handler'].cleanup()
    print("Disconnected safely.")