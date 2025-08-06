import logging
from time import sleep

from android_device_manager import (
    AndroidDevice, AndroidProp,
)
from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.emulator.config import EmulatorConfiguration

logging.basicConfig(level=logging.INFO)
avd_config = AVDConfiguration(
    name="test_avd_from_lib", package="system-images;android-36;google_apis;x86_64"
)

emulator_config = EmulatorConfiguration(
    no_window=True,
)

with AndroidDevice(avd_config, emulator_config=emulator_config) as device:
    api_level = device.get_prop(AndroidProp.API_LEVEL)
    android_version = device.get_prop("ro.build.version.release")
    print(f"API Level: {api_level}, Android: {android_version}")
