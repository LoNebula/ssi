import sys
import time
from unittest.mock import MagicMock

# pynputのエラー回避
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from xdpchandler import *

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    return { 'sensor' : 'Movella DOT 9-ch (Time, Quat, FreeAcc, Status)' }

def initChannel(name, channel, types, opts, vars):
    if name == 'sensor':
        channel.dim = 9        # 1(Time) + 4(Quat) + 3(Acc) + 1(Status) = 9列
        channel.type = types.FLOAT
        channel.sr = 60.0

def connect(opts, vars):
    handler = XdpcHandler()
    if not handler.initialize(): return False
    handler.scanForDots()
    if len(handler.detectedDots()) == 0: return False
    handler.connectDots()
    connected = handler.connectedDots()
    if not connected: return False

    for device in connected:
        device.setOutputRate(60)
        # 【重要】クォータニオンと加速度を含むモードに変更
        device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion)

    vars['handler'] = handler
    vars['connected'] = connected
    vars['mac'] = connected[0].bluetoothAddress()
    vars['start_time'] = time.time()
    vars['last_data'] = [0.0] * 9 # 9要素で初期化
    return True

def read(name, sout, reset, board, opts, vars):
    handler = vars['handler']
    mac = vars['mac']
    
    for i in range(sout.num):
        packet = None
        for _ in range(20):
            if handler.packetsAvailable():
                packet = handler.getNextPacket(mac)
                # クォータニオンと加速度の両方が入っているかチェック
                if packet and packet.containsOrientation() and packet.containsFreeAcceleration():
                    break
            time.sleep(0.001)

        if packet:
            # お手本のCSVの順番通りにデータをパッキング
            time_fine = packet.sampleTimeFine()      # 1: SampleTimeFine
            quat = packet.orientationQuaternion()    # 2-5: W, X, Y, Z
            acc = packet.freeAcceleration()          # 6-8: X, Y, Z
            status = packet.status()                 # 9: Status
            
            vars['last_data'] = [
                float(time_fine),
                quat[0], quat[1], quat[2], quat[3],
                acc[0], acc[1], acc[2],
                float(status)
            ]
        
        # SSIのバッファに9列分書き込み
        current = vars['last_data']
        for d in range(9):
            sout[i, d] = current[d]

def disconnect(opts, vars):
    if 'connected' in vars:
        for device in vars['connected']:
            device.stopMeasurement()
    if 'handler' in vars:
        vars['handler'].cleanup()