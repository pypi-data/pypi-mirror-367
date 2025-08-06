from android_device_manager import (
    AndroidDevice,
    EmulatorConfiguration,
)

from android_device_manager.avd.config import AVDConfiguration

avd_config = AVDConfiguration(
    name="test_avd_from_lib", package="system-images;android-36;google_apis;x86_64"
)

emulator_config = EmulatorConfiguration(
    no_window=True,
)

with AndroidDevice(avd_config) as device:
    print(device.name)
