
import sys
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

AT_COMMANDS_HL78 =[
    "ATI",
    "AT+CMEE=1",
    "AT+KSRAT?",
    "AT+KBNDCFG?",
    "AT+CIMI",
    "AT+CPIN?",
    "AT+CCID?",
    "AT+CGSN",
    "AT+HWREV",
    "AT+CGDCONT?",
    "AT+KCARRIERCFG?",
    "AT+CEDRXS?",
    "AT+CPSMS?",
    "AT+KSIMDET?",
    "AT+KSIMSEL?",
    "AT+CREG?",
    "AT+CEREG?",
    "AT+KUSBCOMP?",
    "AT&V",
    "AT+IPR?",
    "AT+CSQ",
    "AT+KSLEEP?",
    "AT+KNWSCANCFG?",
    "AT+KTEMPMON?",
    "AT+KCERTSTORE?",
    "AT+KTCPCFG?",
    "AT+KUDPCFG?",
    "AT+KIPOPT?",
    "AT+WDSC?",
    "AT+WDSG",
    "AT+NVBU=2",
    "AT+COPS?"
]

AT_COMMAND_COPS = "AT+COPS=?"

def animate_spinner() -> None:
    """
    Animates a simple spinner character to indicate an ongoing operation.
    """
    chars = '|/-\\'
    for char in chars:
        sys.stdout.write(f'\rReading {char}')
        sys.stdout.flush()
        time.sleep(0.05)

def send_at_command(port: str, command: str, timeout: float = 60, baudrate: int = 115200) -> str:
    result = ""
    start_time = time.time()
    try:
        with serial.Serial(port, baudrate, timeout=0.5) as console:
            logging.debug(f"Sending command: {command}")
            console.write(f"{command}\r\n".encode("utf-8"))
            while time.time() - start_time < timeout:
                chunk = console.read(1024).decode("utf-8")
                result += chunk
                if "OK\r\n" in result or "ERROR\r\n" in result:
                    break
                animate_spinner()
    except Exception as e:
        logging.error(f"Error sending command: {e}")
    finally:
        sys.stdout.write('\r' + ' ' * 20 + '\r')  # Clear the spinner line
        sys.stdout.flush()
    return "\n".join(line.strip() for line in result.splitlines() if line.strip())

def get_module_status(port: str, search: int, model: str, baudrate: int = 115200) -> str:
    """
    Retrieves the status of an module using AT commands.
    """
    result = ""
    try:
        commands = AT_COMMANDS_HL78 if model.lower() == "hl78xx" else AT_COMMANDS
        result = "\n\n".join(send_at_command(port, command, baudrate=baudrate).strip() for command in commands)
        if search:
            result += "\n\n" +  get_em_cops(port)
    except Exception as e:
        logging.error(f"Error getting module status: {e}")
    return result

def get_em_cops(port: str, baudrate: int = 115200) -> str:
    """
    Retrieves the status of an EM9xxx module using AT commands.
    """
    result = ""
    try:

        logging.info(f"Sending command: {AT_COMMAND_COPS},wait for finishing")
        result = "".join(send_at_command(port, AT_COMMAND_COPS, 120, baudrate).strip())
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

def start_process(port: str, model: str, log_level: int, search: int, baudrate: int = 115200) -> None:
    """
    Main function to retrieve the status of an EM9xxx module using AT commands.
    """
    logging.basicConfig(level=log_level)
    logging.info(f"Starting process for port {port} with model {model} and baudrate {baudrate}")
    result  = get_module_status(port, search, model, baudrate)
    if result:
        creat_status_file(result, model)
    else:
        logging.error("No result received from the module.")
