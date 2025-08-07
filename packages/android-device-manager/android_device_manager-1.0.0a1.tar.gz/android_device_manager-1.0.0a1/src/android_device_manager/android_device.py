import logging
import subprocess
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Optional, List, Union, Dict


from .adb.client import AdbClient
from .adb.exceptions import ADBError
from .avd.config import AVDConfiguration
from .avd.exceptions import AVDCreationError, AVDDeletionError
from .avd.manager import AVDManager
from .constants import AndroidProp
from .emulator.config import EmulatorConfiguration
from .emulator.exceptions import EmulatorStartError
from .emulator.manager import EmulatorManager
from .exceptions import AndroidDeviceError

from .utils.android_sdk import AndroidSDK

logger = logging.getLogger(__name__)


class AndroidDeviceState(Enum):
    """
    Enumeration of possible states for an AndroidDevice.

    Attributes:
        NOT_CREATED: The AVD does not exist yet.
        CREATED: The AVD exists but the emulator is not running.
        RUNNING: The emulator is running and fully booted.
        STOPPED: The emulator was running but is now stopped.
        ERROR: An error occurred during an operation.
    """

    NOT_CREATED = "not_created"
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class AndroidDevice:
    def __init__(
        self,
        avd_config: AVDConfiguration,
        emulator_config: Optional[EmulatorConfiguration] = None,
        android_sdk: Optional[AndroidSDK] = None,
    ):
        self._avd_config = avd_config
        self._emulator_config = emulator_config
        self.state = AndroidDeviceState.NOT_CREATED

        self._android_sdk = android_sdk or AndroidSDK()
        self._avd_manager = AVDManager(self._android_sdk)
        self._emulator_manager = EmulatorManager(self._android_sdk)
        self._adb_client: Optional[AdbClient] = None

    @property
    def name(self) -> str:
        """
        The name of the managed AVD.

        Returns:
            str: The name of the AVD.
        """
        return self._avd_config.name

    def create(self, force: bool = False) -> None:
        """
        Create the AVD if it does not exist.

        Args:
            force (bool): If True, overwrite any existing AVD with the same name.

        Raises:
            AVDCreationError: If the AVD cannot be created.
        """
        logger.info(f"Creating AVD '{self.name}'...")
        try:
            if not self._avd_manager.exist(self.name):
                self._avd_manager.create(self._avd_config, force=force)
                self.state = AndroidDeviceState.CREATED
                logger.info(f"AVD '{self.name}' created.")
            else:
                logger.info(f"AVD '{self.name}' already exists.")
                self.state = AndroidDeviceState.CREATED
        except AVDCreationError as e:
            self.state = AndroidDeviceState.ERROR
            raise e
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to create AVD '{self.name}': {e}")
            raise AVDCreationError(self.name, f"Failed to create AVD : {e}") from e

    def start(self):
        """
        Start the emulator for the current AVD and wait for it to boot.

        Raises:
            EmulatorStartError: If the emulator fails to start.
            ADBError: If there is an error communicating with the device.
            TimeoutError: If the emulator does not boot within the allowed time.
        """
        logger.info(f"Starting emulator for AVD '{self.name}'...")
        try:
            port = self._emulator_manager.start_emulator(
                avd_name=self.name,
                emulator_config=self._emulator_config,
            )
            self._adb_client = AdbClient(port, self._android_sdk)
            self._adb_client.wait_for_boot()
            self.state = AndroidDeviceState.RUNNING
            logger.info(f"Emulator for AVD '{self.name}' is running (port {port}).")
        except (EmulatorStartError, ADBError, TimeoutError) as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to start emulator for '{self.name}': {e}")
            raise

    def stop(self):
        """
        Stop the running emulator and release resources.

        Raises:
            Exception: If stopping the emulator fails.
        """
        logger.info(f"Stopping emulator for AVD '{self.name}'...")
        try:
            if self._adb_client:
                self._adb_client.kill_emulator()
                self._adb_client = None
            self._emulator_manager.stop_emulator()
            self.state = AndroidDeviceState.STOPPED
            logger.info(f"Emulator for AVD '{self.name}' stopped.")
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to stop emulator for '{self.name}': {e}")
            raise

    def delete(self):
        """
        Delete the AVD.

        Raises:
            AVDDeletionError: If deletion fails.
        """
        logger.info(f"Deleting AVD '{self.name}'...")
        try:
            self._avd_manager.delete(self.name)
            self.state = AndroidDeviceState.NOT_CREATED
            logger.info(f"AVD '{self.name}' deleted.")
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to delete AVD '{self.name}': {e}")
            raise AVDDeletionError(self.name, f"Failed to delete AVD: {e}") from e

    def root(self) -> bool:
        """
        Attempt to restart adbd as root and sync state.

        Returns:
            bool: True if device is now root, False otherwise.
        """
        self._ensure_running()
        return self._adb_client.root()

    def unroot(self) -> bool:
        self._ensure_running()
        return self._adb_client.unroot()

    def is_root(self):
        self._ensure_running()
        return self._adb_client.is_root()

    def get_prop(
        self, key: Union[str, AndroidProp], timeout: int = 10, check: bool = True
    ) -> str:
        self._ensure_running()
        return self._adb_client.get_prop(key, timeout=timeout, check=check)

    def get_all_props(self, timeout: int = 10) -> Dict[str, str]:
        self._ensure_running()
        return self._adb_client.get_all_props(timeout=timeout)

    def list_installed_packages(self) -> List[str]:
        self._ensure_running()
        return self._adb_client.list_installed_packages()

    def is_package_installed(self, package_name: str) -> bool:
        self._ensure_running()
        return package_name in self._adb_client.list_installed_packages()

    def install_apk(self, apk_path: str, timeout: int = 30) -> None:
        self._ensure_running()
        self._adb_client.install_apk(apk_path, timeout=timeout)

    def uninstall_package(self, package_name: str, keep_data: bool = False) -> None:
        """
        Uninstall a package from the device.

        Args:
            package_name (str): Package to uninstall.
            keep_data (bool): If True, keep app data and cache.

        Raises:
            AndroidDeviceError: If device not started or package not installed.
            ADBError: On failure.
        """
        self._ensure_running()
        if not self.is_package_installed(package_name):
            raise AndroidDeviceError(f"Package '{package_name}' is not installed.")
        self._adb_client.uninstall_package(package_name, keep_data=keep_data)

    def push_file(self, local: str | Path, remote: str) -> None:
        self._ensure_running()
        self._adb_client.push_file(local, remote)

    def pull_file(self, remote: str, local: str | Path) -> None:
        self._ensure_running()
        self._adb_client.pull_file(remote, local)

    def pull_data_partition(self, dest_path: str | Path = "./data.tar"):
        self._ensure_running()
        self._adb_client.root()
        self._adb_client._run_adb_command(["shell", "stop"])
        self._adb_client.shell(
            ["tar", "cf", "/tmp/data.tar", "/data"], check=False, timeout=120
        )
        self._adb_client.pull_file("/tmp/data.tar", dest_path)
        self._adb_client.shell(["rm", "-r", "/tmp/data.tar"])
        self._adb_client._run_adb_command(["shell", "start"])
        self._adb_client.unroot()

    def get_logcat(self, filter_spec: Optional[List[str]] = None) -> str:
        """
        Get the device logcat output.

        Args:
            filter_spec (Optional[List[str]]): Filter spec(s), e.g., ['*:E']

        Returns:
            str: The log output.
        """
        self._ensure_running()
        return self._adb_client.get_logcat(filter_spec=filter_spec)

    def clear_logcat(self) -> None:
        """
        Clear the device logcat buffer.

        Raises:
            ADBError: On failure.
        """
        self._ensure_running()
        self._adb_client.clear_logcat()

    def shell(
        self, args: List[str], timeout: int = 30, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Execute a shell command on the device/emulator via ADB.

        Args:
            args (List[str]): The shell command as a list of arguments. Example: ["ls", "/sdcard"]
            timeout (int): Timeout for the command (default: 30).
            check (bool): If True, raise an exception for non-zero exit code.

        Returns:
            subprocess.CompletedProcess: The result object (stdout, stderr, etc.).

        Raises:
            AndroidDeviceError: If the command is forbidden (e.g., stop, reboot, poweroff).
            ADBError: If the command fails (and check=True).
            AVDTimeoutError: On timeout.
        """
        forbidden = {"stop", "reboot", "poweroff"}
        if args and args[0] in forbidden:
            raise AndroidDeviceError(
                f"The shell command '{args[0]}' is not allowed via shell(). "
                "Such commands can cause the device state to become incoherent with the library state. "
                "Direct use of stop/reboot/poweroff is not supported yet—please use explicit API methods."
            )
        return self._adb_client.shell(args, timeout=timeout, check=check)

    def _ensure_running(self):
        if self.state != AndroidDeviceState.RUNNING or not self._adb_client:
            raise AndroidDeviceError(
                "ADB client not initialized. Device must be started."
            )

    def __enter__(self):
        """
        Context manager entry: ensure device is created and started.
        """
        if self.state == AndroidDeviceState.NOT_CREATED:
            self.create()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit: stop the emulator and (optionally) delete the AVD.
        """
        try:
            self.stop()
        except Exception as e:
            logger.warning(f"Error while stopping emulator: {e}")
        try:
            self.delete()
        except Exception as e:
            logger.warning(f"Error while deleting AVD: {e}")
