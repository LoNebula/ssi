import sys
import time
from unittest.mock import MagicMock

# SSI環境でクラッシュする pynput をダミー化
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from xdpchandler import *

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    return { 'sensor' : 'Movella DOT Orientation' }

def initChannel(name, channel, types, opts, vars):
    if name == 'sensor':
        channel.dim = 3
        channel.type = types.FLOAT
        channel.sr = 60.0

def connect(opts, vars):
    handler = XdpcHandler()
    if not handler.initialize():
        return False

    handler.scanForDots()
    if len(handler.detectedDots()) == 0:
        print("No devices detected.")
        return False

    # メソッド名を修正: connectDots() 
    # これによりスキャンで見つかったすべてのドットに接続を試みます
    handler.connectDots()
    connected = handler.connectedDots()
    
    if len(connected) == 0:
        print("Failed to connect.")
        return False

    # 1台目のデバイスを使用
    device = connected[0]
    device.setOutputRate(60)
    device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
    device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler)

    vars['handler'] = handler
    vars['device'] = device
    vars['mac'] = device.bluetoothAddress()
    vars['start_time'] = time.time()
    vars['reset_done'] = False
    print(f"Successfully connected and started: {vars['mac']}")
    return True

def read(name, sout, reset, board, opts, vars):
    handler = vars['handler']
    mac = vars['mac']
    device = vars['device']
    
    # 5秒後のHeading Reset（これはそのまま）
    if not vars.get('reset_done', False) and (time.time() - vars['start_time'] > 5.0):
        device.resetOrientation(movelladot_pc_sdk.XRM_Heading)
        print("\nHeading Reset Done.")
        vars['reset_done'] = True

    # 指定されたサンプル数（sout.num）を埋める
    for i in range(sout.num):
        packet = None
        # 無限ループにならないよう、少しだけ試行する
        tries = 0
        while packet is None and tries < 100:
            if handler.packetsAvailable():
                packet = handler.getNextPacket(mac)
                if not packet or not packet.containsOrientation():
                    packet = None
            else:
                time.sleep(0.001)
            tries += 1
        
        if packet:
            # データが取れた場合
            euler = packet.orientationEuler()
            sout[i, 0] = euler.x()
            sout[i, 1] = euler.y()
            sout[i, 2] = euler.z()
        else:
            # データが取れなかった場合、前回の値を維持するか0を入れる
            # ここではSSIのフリーズを防ぐために0を入れます
            sout[i, 0] = 0.0
            sout[i, 1] = 0.0
            sout[i, 2] = 0.0

def disconnect(opts, vars):
    if 'device' in vars:
        vars['device'].stopMeasurement()
    if 'handler' in vars:
        vars['handler'].cleanup()
    print("Disconnected safely.")