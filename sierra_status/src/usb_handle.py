import sys
import time
import serial
import logging

from sierra_status.src.conf import (
    AT_COMMANDS,
    AT_COMMANDS_HL78,
    AT_COMMAND_COPS,
    DEFAULT_TIMEOUT,
    DEFAULT_BAUDRATE,
    STATUS_FILE_PATTERN,
)


def animate_spinner() -> None:
    """
    Animates a simple spinner character to indicate an ongoing operation.
    """
    chars = "|/-\\"
    for char in chars:
        sys.stdout.write(f"\rReading {char}")
        sys.stdout.flush()
        time.sleep(0.05)


def send_at_command(
    port: str,
    command: str,
    timeout: float = DEFAULT_TIMEOUT,
    baudrate: int = DEFAULT_BAUDRATE,
) -> str:
    """
    Sends an AT command to the specified serial port and returns the response.

    Args:
        port (str): The serial port to use.
        command (str): The AT command to send.
        timeout (float, optional): The maximum time to wait for a response, in seconds. Defaults to 60.
        baudrate (int, optional): The baud rate to use for the serial connection. Defaults to 115200.

    Returns:
        str: The response from the AT command, with each line stripped of leading/trailing whitespace.
    """
    if not port or not command:
        raise ValueError("Port and command must be provided")
    if baudrate <= 0:
        raise ValueError("Baudrate must be a positive integer")

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
    except serial.SerialException as e:
        logging.error(f"Serial communication error: {e}")
    except ValueError as e:
        logging.error(f"Value error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        sys.stdout.write("\r" + " " * 20 + "\r")  # Clear the spinner line
        sys.stdout.flush()
    return "\n".join(line.strip() for line in result.splitlines() if line.strip())


def get_module_status(
    port: str, search: int, model: str, baudrate: int = 115200
) -> str:
    """
    Retrieves the status of an module using AT commands.

    Args:
        port (str): The serial port to use.
        search (int): A flag indicating whether to retrieve additional status information using the AT+COPS command.
        model (str): The model of the module.
        baudrate (int, optional): The baud rate to use for the serial connection. Defaults to 115200.

    Returns:
        str: The status information retrieved from the module.
    """
    result = ""
    try:
        commands = AT_COMMANDS_HL78 if model.lower() == "hl78xx" else AT_COMMANDS
        result = "\n\n".join(
            send_at_command(port, command, baudrate=baudrate).strip()
            for command in commands
        )
        if search:
            result += f"\n\n{get_em_cops(port)}"
    except Exception as e:
        logging.error(f"Error getting module status: {e}")
    return result


def get_em_cops(port: str, baudrate: int = DEFAULT_BAUDRATE) -> str:
    """
    Retrieves the status of an EM9xxx module using the AT+COPS command.

    Args:
        port (str): The serial port to use.
        baudrate (int, optional): The baud rate to use for the serial connection. Defaults to the DEFAULT_BAUDRATE.

    Returns:
        str: The status information retrieved from the module.
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

    Args:
        result (str): The status information to be written to the file.
        model (str): The model of the module.

    Returns:
        None
    """
    try:
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_name = STATUS_FILE_PATTERN.format(model=model, timestamp=time_stamp)
        with open(file_name, "w") as f:
            f.write(result)
        logging.info(f"Status file created: {file_name}")
    except Exception as e:
        logging.error(f"Error creating status file: {e}")


def get_interactive_command() -> str:
    """
    Gets and validates an AT command from user input.

    Returns:
        str: Validated AT command or empty string to exit
    """
    command = input("Enter AT command: ").strip()
    if command.lower() == "exit":
        return ""

    if not command.upper().startswith("AT"):
        logging.error("Command must start with 'AT'")
        return get_interactive_command()

    return command


def handle_interactive_session(port: str, baudrate: int, model: str) -> None:
    """
    Manages an interactive AT command session
    """
    logging.info("Interactive AT Command Mode (type 'exit' to quit)")
    result = ""

    while True:
        command = get_interactive_command()
        if not command:
            logging.info("Exiting interactive mode")
            break

        response = send_at_command(port, command, DEFAULT_TIMEOUT, baudrate)
        result += f"\n=== Command: {command} ===\n{response}\n"
        logging.info(response)

    if result:
        creat_status_file(result, f"{model}_interactive")


def start_process(
    port: str,
    model: str,
    log_level: int,
    search: int,
    baudrate: int = DEFAULT_BAUDRATE,
    interactive: bool = False,
) -> None:
    """
    Main function to retrieve the status of an EM9xxx module using AT commands.

    Args:
        port (str): The serial port to use.
        model (str): The model of the module.
        log_level (int): The logging level to use.
        search (int): The search parameter to use.
        baudrate (int, optional): The baud rate to use for the serial connection.
        interactive (bool, optional): Run in interactive mode if True.
    returns:
        None
    """
    start_time = time.time()
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info(
        f"""Start time: {time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())} 
            Starting process for port {port} 
            with model {model} and baudrate {baudrate}"""
    )

    if interactive:
        handle_interactive_session(port, baudrate, model)
    else:
        result = get_module_status(port, search, model, baudrate)
        if result:
            time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            result = f"Finished time: {time_stamp}\n" + result
            creat_status_file(result, model)
        else:
            logging.error("No result received from the module.")

    logging.info(
        f"Total time for running this script: {time.time() - start_time:.2f} seconds"
    )
