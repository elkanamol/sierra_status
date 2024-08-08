
import time
import serial
import logging
AT_COMMANDS = [
    "ATI",
    "AT+CMEE=1",
    "AT!PRIID?",
    "AT!IMAGE?",
    "ATI8",
    "AT!GSTATUS?",
    "AT+CPIN?",
    "AT+CIMI",
    "AT!PCINFO?",
    "AT!CUSTOM?",
    "AT+CREG?",
    "AT+CGREG?",
    "AT+CEREG?",
    "AT+CGPADDR=1",
    "AT!SELRAT?",
    "AT+CGDCONT?",
    "AT!UIMS?",
    "AT!IMPREF?",
    "AT!BAND?",
    'AT!ENTERCND="A710"',
    "AT!BAND?",
    "AT!HWID?",
    "AT!USBCOMP?",
    "AT!USBSPEED?",
    "AT!USBPID?",
    "AT!USBINFO?",
    "AT!LTEINFO?",
    "AT!NRINFO?",
    "AT+COPS?"
]

AT_COMMAND_COPS = "AT!COPS=?"

def send_at_command(port: str , command: str, time_to_sleep: float = 0.2) -> str:
    """
    Sends an AT command to the specified serial port and returns the response.  
    """
    result, raw_result = "", ""
    try:
        command_to_send = f"{command}\r\n"
        logging.debug(f"Sending command: {command}")
        console = serial.Serial(port, 115200, timeout=2)
        console.write(command_to_send.encode("utf-8"))
        time.sleep(time_to_sleep)
        raw_result = console.read_until(b"OK\r\n" or b"ERROR\r\n").decode("utf-8")
        result ="\n".join(line.strip() for line in raw_result.splitlines() if line.strip())
        console.close()
    except Exception as e:
        logging.error(f"Error sending command: {e}")
    return result

def get_em_status(port: str, search: int) -> str:
    """
    Retrieves the status of an EM9xxx module using AT commands.
    """
    result = ""
    try:
        result = "\n\n".join(send_at_command(port, command).strip() for command in AT_COMMANDS)
        if search:
            result += get_em_cops(port)
    except Exception as e:
        logging.error(f"Error getting EM9 status: {e}")
    return result

def get_em_cops(port: str) -> str:
    """
    Retrieves the status of an EM9xxx module using AT commands.
    """
    result = ""
    try:
        logging.info(f"Sending command: {AT_COMMAND_COPS},wait for finishing")
        result = send_at_command(port, AT_COMMAND_COPS, 60)
    except Exception as e:
        logging.error(f"Error getting EM9 status: {e}")
    return result

def creat_status_file(result: str, model: str) -> None:
    """
    Creates a status file with the provided result.
    """
    try:
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        with open(f"status_{model}_{time_stamp}.txt", "w") as f:
            f.write(result)
        logging.info(f"Status file created: status_{model}_{time_stamp}.txt")
    except Exception as e:
        logging.error(f"Error creating status file: {e}")

def start_process(port: str, model: str, log_level: int, search: int) -> None:
    """
    Main function to retrieve the status of an EM9xxx module using AT commands.
    """
    logging.basicConfig(level=log_level)
    logging.info(f"Starting process for port {port}")
    result  = get_em_status(port, search)
    if result:
        creat_status_file(result, model)
    else:
        logging.error("No result received from the module.")

    


        