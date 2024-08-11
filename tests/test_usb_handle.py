import logging
import unittest
from unittest.mock import mock_open, patch, MagicMock

from sierra_status.src.usb_handle import AT_COMMAND_COPS, AT_COMMANDS, creat_status_file, get_em_cops, get_em_status, send_at_command, start_process

class TestATCommands(unittest.TestCase):

    def test_at_commands_list_not_empty(self):
        self.assertTrue(len(AT_COMMANDS) > 0)

    def test_at_commands_are_strings(self):
        for command in AT_COMMANDS:
            self.assertIsInstance(command, str)

    def test_at_commands_start_with_at(self):
        for command in AT_COMMANDS:
            self.assertTrue(command.startswith("AT"))

    def test_specific_commands_present(self):
        expected_commands = ["ATI", "AT+CMEE=1", "AT!GSTATUS?", "AT+CPIN?"]
        for command in expected_commands:
            self.assertIn(command, AT_COMMANDS)

    def test_enter_cnd_command_format(self):
        enter_cnd_command = 'AT!ENTERCND="A710"'
        self.assertIn(enter_cnd_command, AT_COMMANDS)

    def test_at_commands_uppercase(self):
        for command in AT_COMMANDS:
            self.assertEqual(command, command.upper())

class TestUSBHandle(unittest.TestCase):

    def setUp(self):
        self.mock_port = "COM1"
        self.mock_command = "AT+TEST"
        self.mock_result = "OK\r\n"

    @patch('sierra_status.src.usb_handle.serial.Serial')
    def test_send_at_command_success(self, mock_serial):
        mock_serial.return_value.read_until.return_value = self.mock_result.encode('utf-8')
        result = send_at_command(self.mock_port, self.mock_command)
        self.assertEqual(result, "OK")

    @patch('sierra_status.src.usb_handle.serial.Serial')
    def test_send_at_command_exception(self, mock_serial):
        mock_serial.side_effect = Exception("Test exception")
        result = send_at_command(self.mock_port, self.mock_command)
        self.assertEqual(result, "")

    @patch('sierra_status.src.usb_handle.send_at_command')
    def test_get_em_status_without_search(self, mock_send_at_command):
        mock_send_at_command.return_value = "Test Result"
        result = get_em_status(self.mock_port, 0)
        self.assertIn("Test Result", result)
        self.assertNotIn(AT_COMMAND_COPS, result)

    @patch('sierra_status.src.usb_handle.send_at_command')
    @patch('sierra_status.src.usb_handle.get_em_cops')
    def test_get_em_status_with_search(self, mock_get_em_cops, mock_send_at_command):
        mock_send_at_command.return_value = "Test Result"
        mock_get_em_cops.return_value = "COPS Result"
        result = get_em_status(self.mock_port, 1)
        self.assertIn("Test Result", result)
        self.assertIn("COPS Result", result)

    @patch('sierra_status.src.usb_handle.send_at_command')
    def test_get_em_cops(self, mock_send_at_command):
        mock_send_at_command.return_value = "COPS Test Result"
        result = get_em_cops(self.mock_port)
        self.assertEqual(result, "COPS Test Result")
        mock_send_at_command.assert_called_with(self.mock_port, AT_COMMAND_COPS, 60)

    @patch('builtins.open', new_callable=mock_open)
    @patch('sierra_status.src.usb_handle.time.strftime')
    def test_creat_status_file(self, mock_strftime, mock_file):
        mock_strftime.return_value = "20230101_120000"
        creat_status_file("Test Status", "TestModel")
        mock_file.assert_called_with("status_TestModel_20230101_120000.txt", "w")
        mock_file().write.assert_called_with("Test Status")

    @patch('sierra_status.src.usb_handle.get_em_status')
    @patch('sierra_status.src.usb_handle.creat_status_file')
    def test_start_process_with_result(self, mock_creat_status_file, mock_get_em_status):
        mock_get_em_status.return_value = "Test Status"
        start_process(self.mock_port, "TestModel", logging.INFO, 0)
        mock_creat_status_file.assert_called_with("Test Status", "TestModel")

    @patch('sierra_status.src.usb_handle.get_em_status')
    @patch('sierra_status.src.usb_handle.creat_status_file')
    def test_start_process_without_result(self, mock_creat_status_file, mock_get_em_status):
        mock_get_em_status.return_value = ""
        start_process(self.mock_port, "TestModel", logging.INFO, 0)
        mock_creat_status_file.assert_not_called()


if __name__ == '__main__':
    unittest.main()