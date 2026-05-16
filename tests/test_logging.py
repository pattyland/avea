import unittest
from unittest.mock import Mock

from bleak.exc import BleakError

from avea.avea import Bulb, MANUFACTURER_NAME_UUID, check_bounds


class FirmwareClient:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.uuid = None

    async def read_gatt_char(self, uuid):
        self.uuid = uuid
        if self.error:
            raise self.error
        return self.payload


class LoggingTests(unittest.IsolatedAsyncioTestCase):
    def test_check_bounds_logs_invalid_string(self):
        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(check_bounds("abc"), 0)

        self.assertIn("was not a number", "\n".join(logs.output))

    def test_check_bounds_logs_none(self):
        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(check_bounds(None), 0)

        self.assertIn("was not a number", "\n".join(logs.output))

    async def test_read_firmware_version_logs_bleak_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb._client = FirmwareClient(error=BleakError("read failed"))

        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(await bulb._read_firmware_version(), "")

        self.assertIn("Could not read firmware version", "\n".join(logs.output))

    async def test_read_firmware_version_logs_decode_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb._client = FirmwareClient(payload=bytearray(b"\xff"))

        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(await bulb._read_firmware_version(), "")

        self.assertIn("Could not decode firmware version", "\n".join(logs.output))

    async def test_read_manufacturer_name_reads_expected_uuid(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb._client = FirmwareClient(payload=bytearray(b"Elgato Systems GmbH"))

        self.assertEqual(await bulb._read_manufacturer_name(), "Elgato Systems GmbH")
        self.assertEqual(bulb._client.uuid, MANUFACTURER_NAME_UUID)

    async def test_read_manufacturer_name_logs_bleak_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb._client = FirmwareClient(error=BleakError("read failed"))

        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(await bulb._read_manufacturer_name(), "")

        self.assertIn("Could not read manufacturer name", "\n".join(logs.output))

    async def test_read_manufacturer_name_logs_decode_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb._client = FirmwareClient(payload=bytearray(b"\xff"))

        with self.assertLogs("avea.avea", level="WARNING") as logs:
            self.assertEqual(await bulb._read_manufacturer_name(), "")

        self.assertIn("Could not decode manufacturer name", "\n".join(logs.output))

    def test_smooth_transition_masks_expected_connection_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb.get_color = Mock(side_effect=BleakError("not connected"))

        with self.assertLogs("avea.avea", level="WARNING") as logs:
            bulb.set_smooth_transition(1, 2, 3)

        self.assertIn("Could not read current color", "\n".join(logs.output))

    def test_smooth_transition_propagates_unexpected_error(self):
        bulb = Bulb("00:11:22:33:44:55")
        bulb.get_color = Mock(side_effect=RuntimeError("bug"))

        with self.assertRaises(RuntimeError):
            bulb.set_smooth_transition(1, 2, 3)
