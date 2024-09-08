import logging
import unittest
import serial
from unittest.mock import mock_open, patch, MagicMock

from sierra_status.src.conf import (
    AT_COMMAND_COPS,
    AT_COMMANDS,
    AT_COMMANDS_HL78,
    DEFAULT_BAUDRATE,
)
from sierra_status.src.usb_handle import (
    animate_spinner,
    creat_status_file,
    get_em_cops,
    get_module_status,
    send_at_command,
    start_process,
)

EXPECTED_COMMANDS = ["ATI", "AT+CMEE=1", "AT!GSTATUS?", "AT+CPIN?"]
ENTER_CND_COMMAND = 'AT!ENTERCND="A710"'


class TestATCommands(unittest.TestCase):
    def test_at_commands_properties(self) -> None:
        for command_list in [AT_COMMANDS, AT_COMMANDS_HL78]:
            with self.subTest(command_list=command_list):
                self.assertTrue(len(command_list) > 0)
                for command in command_list:
                    self.assertIsInstance(command, str)
                    self.assertTrue(command.startswith("AT"))
                    self.assertEqual(command, command.upper())

    def test_specific_commands_present(self) -> None:
        for command in EXPECTED_COMMANDS:
            self.assertIn(command, AT_COMMANDS)

    def test_enter_cnd_command_format(self) -> None:
        self.assertIn(ENTER_CND_COMMAND, AT_COMMANDS)


class TestUSBHandle(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_port = "COM1"
        self.mock_command = "AT+TEST"
        self.mock_result = "OK\r\n"

    def test_send_at_command_success(self) -> None:
        with patch("sierra_status.src.usb_handle.serial.Serial") as mock_serial:
            mock_instance: MagicMock = mock_serial.return_value
            mock_instance.read.return_value = b"OK\r\n"
            result: str = send_at_command(self.mock_port, self.mock_command)
            self.assertEqual(result, "")

    def test_send_at_command_exception(self) -> None:
        with patch(
            "sierra_status.src.usb_handle.serial.Serial",
            side_effect=Exception("Test exception"),
        ):
            result = send_at_command(self.mock_port, self.mock_command)
            self.assertEqual(result, "")

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_without_search(
        self, mock_send_at_command: MagicMock
    ) -> None:
        mock_send_at_command.return_value = "Test Result"
        result = get_module_status(self.mock_port, 0, "EM9xxx")
        self.assertIn("Test Result", result)

    @patch("sierra_status.src.usb_handle.send_at_command")
    @patch("sierra_status.src.usb_handle.get_em_cops")
    def test_get_module_status_with_search(
        self, mock_get_em_cops: MagicMock, mock_send_at_command: MagicMock
    ) -> None:
        mock_send_at_command.return_value = "Test Result"
        mock_get_em_cops.return_value = "COPS Result"
        result = get_module_status(self.mock_port, 1, "EM9xxx")
        self.assertIn("Test Result", result)
        self.assertIn("COPS Result", result)

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_em_cops(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "COPS Test Result"
        result = get_em_cops(self.mock_port)
        self.assertEqual(result, "COPS Test Result")

    @patch("builtins.open", new_callable=mock_open)
    @patch("sierra_status.src.usb_handle.time.strftime")
    def test_creat_status_file(self, mock_strftime, mock_file) -> None:
        mock_strftime.return_value = "20230101_120000"
        creat_status_file("Test Status", "TestModel")
        mock_file.assert_called_with("status_TestModel_20230101_120000.txt", "w")
        mock_file().write.assert_called_with("Test Status")

    @patch("sierra_status.src.usb_handle.get_module_status")
    @patch("sierra_status.src.usb_handle.creat_status_file")
    @patch("sierra_status.src.usb_handle.time.strftime")
    def test_start_process_with_result(
        self, mock_strftime, mock_creat_status_file, mock_get_module_status
    ) -> None:
        mock_get_module_status.return_value = "Test Status"
        mock_strftime.return_value = "20230101_120000"
        start_process(self.mock_port, "TestModel", logging.INFO, 0)
        expected_result = "Finished time: 20230101_120000\nTest Status"
        mock_creat_status_file.assert_called_with(expected_result, "TestModel")

    @patch("sierra_status.src.usb_handle.get_module_status")
    @patch("sierra_status.src.usb_handle.creat_status_file")
    def test_start_process_without_result(
        self, mock_creat_status_file, mock_get_module_status
    ) -> None:
        mock_get_module_status.return_value = ""
        start_process(self.mock_port, "TestModel", logging.INFO, 0)
        mock_creat_status_file.assert_not_called()


class TestAnimateSpinner(unittest.TestCase):
    def test_animate_spinner(self) -> None:
        with patch("sys.stdout") as mock_stdout, patch("time.sleep") as mock_sleep:
            animate_spinner()
            self.assertEqual(mock_stdout.write.call_count, 4)
            self.assertEqual(mock_stdout.flush.call_count, 4)
            self.assertEqual(mock_sleep.call_count, 4)

    def test_animate_spinner_interruption(self) -> None:
        with patch("sys.stdout") as mock_stdout, patch(
            "time.sleep", side_effect=KeyboardInterrupt()
        ):
            with self.assertRaises(KeyboardInterrupt):
                animate_spinner()
            self.assertEqual(mock_stdout.write.call_count, 1)
            self.assertEqual(mock_stdout.flush.call_count, 1)


class TestSendATCommand(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.serial.Serial")
    @patch("sierra_status.src.usb_handle.time.time")
    def test_send_at_command_timeout(self, mock_time, mock_serial) -> None:
        mock_time.side_effect = [0, 61]  # Simulate timeout
        mock_serial.return_value.read.return_value = b""
        result = send_at_command("COM1", "AT+TEST", timeout=60)
        self.assertEqual(result, "")

    @patch("sierra_status.src.usb_handle.serial.Serial")
    def test_send_at_command_error_response(self, mock_serial) -> None:
        mock_serial.return_value.read_until.return_value = b"ERROR\r\n"
        result = send_at_command("COM1", "AT+TEST")
        self.assertEqual(result, "")


class TestGetModuleStatus(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_exception(self, mock_send_at_command) -> None:
        mock_send_at_command.side_effect = Exception("Test exception")
        result = get_module_status("COM1", 0, "EM9xxx")
        self.assertEqual(result, "")

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_all_commands(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "OK"
        result = get_module_status("COM1", 0, "EM9xxx")
        self.assertEqual(result.count("OK"), len(AT_COMMANDS))

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_hl78xx(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "OK"
        result = get_module_status("COM1", 0, "HL78xx")
        self.assertEqual(result.count("OK"), len(AT_COMMANDS_HL78))


class TestCreatStatusFile(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("sierra_status.src.usb_handle.time.strftime")
    def test_creat_status_file_exception(self, mock_strftime, mock_file) -> None:
        mock_strftime.return_value = "20230101_120000"
        mock_file.side_effect = Exception("Test exception")
        with self.assertLogs(level="ERROR") as log:
            creat_status_file("Test Status", "TestModel")
        self.assertIn("Error creating status file", log.output[0])


class TestStartProcess(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.get_module_status")
    @patch("sierra_status.src.usb_handle.creat_status_file")
    @patch("sierra_status.src.usb_handle.logging.basicConfig")
    def test_start_process_log_level(
        self, mock_basicConfig, mock_creat_status_file, mock_get_module_status
    ) -> None:
        mock_get_module_status.return_value = "Test Status"
        start_process("COM1", "TestModel", logging.DEBUG, 0)
        mock_basicConfig.assert_called_with(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    @patch("sierra_status.src.usb_handle.get_module_status")
    @patch("sierra_status.src.usb_handle.creat_status_file")
    @patch("sierra_status.src.usb_handle.logging.error")
    def test_start_process_no_result(
        self, mock_logging_error, mock_creat_status_file, mock_get_module_status
    ) -> None:
        mock_get_module_status.return_value = ""
        start_process("COM1", "TestModel", logging.INFO, 0)
        mock_logging_error.assert_called_with("No result received from the module.")
        mock_creat_status_file.assert_not_called()


class TestSendATCommandAdvanced(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.serial.Serial")
    def test_send_at_command_invalid_port(self, mock_serial) -> None:
        mock_serial.side_effect = serial.SerialException("Invalid port")
        result = send_at_command("INVALID_PORT", "AT+TEST")
        self.assertEqual(result, "")

    def test_send_at_command_empty_port(self) -> None:
        with self.assertRaises(ValueError):
            send_at_command("", "AT+TEST")

    def test_send_at_command_empty_command(self) -> None:
        with self.assertRaises(ValueError):
            send_at_command("COM1", "")

    def test_send_at_command_invalid_baudrate(self) -> None:
        with self.assertRaises(ValueError):
            send_at_command("COM1", "AT+TEST", baudrate=0)


class TestGetModuleStatusAdvanced(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_hl78xx_model(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "HL78xx Response"
        result = get_module_status("COM1", 0, "HL78xx")
        self.assertIn("HL78xx Response", result)
        self.assertEqual(mock_send_at_command.call_count, len(AT_COMMANDS_HL78))

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_module_status_unknown_model(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "Unknown Model Response"
        result = get_module_status("COM1", 0, "UnknownModel")
        self.assertIn("Unknown Model Response", result)
        self.assertEqual(mock_send_at_command.call_count, len(AT_COMMANDS))

    @patch("sierra_status.src.usb_handle.send_at_command")
    @patch("sierra_status.src.usb_handle.get_em_cops")
    def test_get_module_status_with_search_exception(
        self, mock_get_em_cops, mock_send_at_command
    ) -> None:
        mock_send_at_command.return_value = "Test Result"
        mock_get_em_cops.side_effect = Exception("COPS Error")
        result = get_module_status("COM1", 1, "EM9xxx")
        self.assertIn("Test Result", result)
        self.assertNotIn("COPS Error", result)


class TestGetEmCopsAdvanced(unittest.TestCase):
    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_em_cops_timeout(self, mock_send_at_command) -> None:
        mock_send_at_command.side_effect = TimeoutError("Command timed out")
        result = get_em_cops("COM1")
        self.assertEqual(result, "")

    @patch("sierra_status.src.usb_handle.send_at_command")
    def test_get_em_cops_custom_baudrate(self, mock_send_at_command) -> None:
        mock_send_at_command.return_value = "Custom Baudrate Result"
        result = get_em_cops("COM1", baudrate=9600)
        mock_send_at_command.assert_called_with("COM1", AT_COMMAND_COPS, 120, 9600)
        self.assertEqual(result, "Custom Baudrate Result")


class TestCreatStatusFileAdvanced(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("sierra_status.src.usb_handle.time.strftime")
    def test_creat_status_file_unicode_content(self, mock_strftime, mock_file) -> None:
        mock_strftime.return_value = "20230101_120000"
        unicode_content = "Test Status with Unicode: ñáéíóú"
        creat_status_file(unicode_content, "TestModel")
        mock_file.assert_called_with("status_TestModel_20230101_120000.txt", "w")
        mock_file().write.assert_called_with(unicode_content)


if __name__ == "__main__":
    unittest.main()
