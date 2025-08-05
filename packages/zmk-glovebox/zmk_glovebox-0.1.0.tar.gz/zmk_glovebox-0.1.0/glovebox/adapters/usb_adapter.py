"""USB adapter for device detection and flashing operations."""

import logging
import threading
from pathlib import Path

from glovebox.firmware.flash.flash_operations import (
    FlashOperations,
)
from glovebox.firmware.flash.models import BlockDevice, USBDeviceType
from glovebox.protocols.device_detector_protocol import DeviceDetectorProtocol
from glovebox.protocols.usb_adapter_protocol import USBAdapterProtocol
from glovebox.utils.error_utils import create_usb_error


logger = logging.getLogger(__name__)


class USBAdapter:
    """Implementation of USB adapter.

    Note: This class implements USBAdapterProtocol interface.
    """

    def __init__(
        self,
        flash_operations: FlashOperations,
        detector: DeviceDetectorProtocol,
    ) -> None:
        """Initialize the USB adapter."""
        self._detector = detector
        self._flash_ops = flash_operations
        self._lock = threading.RLock()

    @property
    def detector(self) -> DeviceDetectorProtocol:
        """Get the detector instance."""
        return self._detector

    def detect_device(
        self,
        query: str,
        timeout: int = 60,
        initial_devices: list[USBDeviceType] | None = None,
    ) -> USBDeviceType:
        """
        Detect a USB device matching the query.

        Args:
            query: Query string to match devices
            timeout: Maximum time to wait in seconds
            initial_devices: Optional list of devices to exclude from detection

        Returns:
            The first matching USB device

        Raises:
            TimeoutError: If no matching device is found within the timeout
            ValueError: If the query string is invalid
            USBError: If there's an error during device detection
        """
        logger.info("Detecting device with query: %s", query)

        try:
            return self.detector.detect_device(query, timeout, initial_devices)
        except TimeoutError as e:
            error = create_usb_error(
                query,
                "detect_device",
                e,
                {
                    "timeout": timeout,
                    "initial_devices_count": len(initial_devices)
                    if initial_devices
                    else 0,
                },
            )
            logger.error(
                "Device detection timed out after %d seconds for query: %s",
                timeout,
                query,
            )
            raise error from e
        except ValueError as e:
            error = create_usb_error(
                query,
                "detect_device",
                e,
                {
                    "timeout": timeout,
                    "initial_devices_count": len(initial_devices)
                    if initial_devices
                    else 0,
                },
            )
            logger.error("Invalid query for device detection: %s", query)
            raise error from e
        except Exception as e:
            error = create_usb_error(
                query,
                "detect_device",
                e,
                {
                    "timeout": timeout,
                    "initial_devices_count": len(initial_devices)
                    if initial_devices
                    else 0,
                },
            )
            logger.error("Device detection failed: %s", e)
            raise error from e

    def list_matching_devices(self, query: str) -> list[USBDeviceType]:
        """
        List all devices matching the query.

        Args:
            query: Query string to match devices

        Returns:
            List of matching USB device objects

        Raises:
            ValueError: If the query string is invalid
            USBError: If there's an error retrieving devices
        """
        logger.debug("Listing devices matching query: %s", query)

        try:
            return self.detector.list_matching_devices(query)
        except ValueError as e:
            error = create_usb_error(query, "list_matching_devices", e, {})
            logger.error("Invalid query for device listing: %s", query)
            raise error from e
        except Exception as e:
            error = create_usb_error(query, "list_matching_devices", e, {})
            logger.error("Failed to list matching devices: %s", e)
            raise error from e

    def flash_device(
        self,
        device: BlockDevice,
        firmware_file: str | Path,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> bool:
        """
        Flash firmware to a specific device.

        Args:
            device: BlockDevice to flash
            firmware_file: Path to firmware file
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            True if flashing succeeded, False otherwise

        Raises:
            USBError: If firmware file doesn't exist or flashing fails after retries
        """
        firmware_path = Path(firmware_file)
        logger.info("Flashing device %s with firmware: %s", device.name, firmware_path)

        if not firmware_path.exists():
            error = create_usb_error(
                device.name,
                "flash_device",
                FileNotFoundError(f"Firmware file not found: {firmware_path}"),
                {
                    "firmware_path": str(firmware_path),
                    "max_retries": max_retries,
                    "retry_delay": retry_delay,
                    "device_model": device.model
                    if hasattr(device, "model")
                    else "unknown",
                },
            )
            logger.error("Firmware file not found: %s", firmware_path)
            raise error

        try:
            return self._flash_ops.mount_and_flash(
                device, firmware_path, max_retries, retry_delay
            )
        except Exception as e:
            error = create_usb_error(
                device.name,
                "flash_device",
                e,
                {
                    "firmware_path": str(firmware_path),
                    "max_retries": max_retries,
                    "retry_delay": retry_delay,
                    "device_model": device.model
                    if hasattr(device, "model")
                    else "unknown",
                },
            )
            logger.error("Failed to flash device %s: %s", device.name, e)
            raise error from e

    def get_all_devices(self, query: str = "") -> list[USBDeviceType]:
        """
        Get all available USB devices, optionally filtered by query.

        Args:
            query: Optional query string to filter devices

        Returns:
            List of all USB device objects

        Raises:
            USBError: If there's an error retrieving devices
        """
        logger.debug("Getting all block devices")

        try:
            if query:
                return self.detector.list_matching_devices(query)
            else:
                return self.detector.get_devices()
        except Exception as e:
            error = create_usb_error("all", "get_all_devices", e, {"query": query})
            logger.error("Failed to get block devices: %s", e)
            raise error from e

    def mount_device(self, device: BlockDevice) -> list[str]:
        """
        Mount a block device and return the mount points.

        Args:
            device: BlockDevice to mount

        Returns:
            List of mount points

        Raises:
            USBError: If there's an error mounting the device
        """
        logger.debug("Mounting device: %s", device.name)

        # Check if device already has mount points
        if device.mountpoints:
            mount_points = list(device.mountpoints.values())
            logger.debug("Device already mounted at: %s", mount_points)
            return mount_points

        try:
            mount_points = self._flash_ops._os_adapter.mount_device(device)
            return mount_points
        except Exception as e:
            error = create_usb_error(device.name, "mount", e)
            logger.error("Failed to mount device %s: %s", device.name, e)
            raise error from e

    def unmount_device(self, device: BlockDevice) -> bool:
        """
        Unmount a block device.

        Args:
            device: BlockDevice to unmount

        Returns:
            True if successful, False otherwise

        Raises:
            USBError: If there's an error unmounting the device
        """
        logger.debug("Unmounting device: %s", device.name)

        try:
            return self._flash_ops._os_adapter.unmount_device(device)
        except Exception as e:
            error = create_usb_error(device.name, "unmount", e)
            logger.error("Failed to unmount device %s: %s", device.name, e)
            raise error from e

    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        Copy a file from source to destination.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            True if successful, False otherwise

        Raises:
            USBError: If there's an error copying the file
        """
        logger.debug("Copying file from %s to %s", source, destination)
        try:
            # If destination is a directory, copy to the parent directory
            if destination.is_dir():
                return self._flash_ops._os_adapter.copy_firmware_file(
                    source, str(destination)
                )
            else:
                # Use traditional file copy for direct file-to-file copying
                import shutil

                shutil.copy2(source, destination)
                return True
        except Exception as e:
            # Extract device identifier from destination path (mount point)
            device_id = (
                str(destination.parent.name) if destination.parent else "unknown"
            )
            error = create_usb_error(
                device_id,
                "copy_file",
                e,
                {"source": str(source), "destination": str(destination)},
            )
            logger.error(
                "Failed to copy file from %s to %s: %s", source, destination, e
            )
            raise error from e


def create_usb_adapter(
    flash_operations: FlashOperations,
    detector: DeviceDetectorProtocol,
) -> USBAdapterProtocol:
    """Factory function to create a USBAdapter instance with explicit dependencies.

    Args:
        flash_operations: Required FlashOperations instance for flash operations
        detector: Required DeviceDetectorProtocol for device detection operations

    Returns:
        Configured USBAdapter instance

    Example:
        >>> flash_ops = create_flash_operations(create_linux_flash_adapter())
        >>> detector = create_device_detector(create_usb_monitor(), MountPointCache())
        >>> adapter = create_usb_adapter(flash_ops, detector)
        >>> devices = adapter.get_all_devices()
        >>> print(f"Found {len(devices)} devices")
    """
    adapter = USBAdapter(flash_operations=flash_operations, detector=detector)
    return adapter  # type: ignore[return-value]
