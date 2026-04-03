import asyncio
from open_gopro import WirelessGoPro
from open_gopro.models import constants

async def main():
    # interfaces={WirelessGoPro.Interface.BLE} を指定して、
    # エラーの出るWi-Fi接続をスキップします。
    async with WirelessGoPro(interfaces={WirelessGoPro.Interface.BLE}) as gopro:
        print("GoProにBluetoothで接続しました。")

        # 録画開始
        print("録画を開始します...")
        await gopro.ble_setting.shutter.set(constants.Toggle.ENABLE)

        await asyncio.sleep(5)

        # 録画停止
        print("録画を停止します...")
        await gopro.ble_setting.shutter.set(constants.Toggle.DISABLE)

if __name__ == "__main__":
    asyncio.run(main())