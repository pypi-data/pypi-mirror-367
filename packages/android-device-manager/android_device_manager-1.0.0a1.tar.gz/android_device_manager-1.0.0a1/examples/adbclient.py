from android_device_manager.adb.client import AdbClient
from android_device_manager.utils.android_sdk import AndroidSDK

adb = AdbClient(5554)

adb.kill_emulator()