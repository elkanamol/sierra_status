import argparse
import logging
import sys
import os

from sierra_status.__version__ import __version__
from sierra_status.src import usb_handle

DEFAULT_BAUDRATE = 115200


def setup_logging(verbose: bool) -> None:
    """
    Sets up the logging configuration based on the provided verbosity level.

    Args:
        verbose (bool): If True, sets the log level to DEBUG, otherwise sets it to INFO.

    Returns:
        None
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level)


def validate_port(port: str) -> None:
    """
    Validates that the specified USB port exists on the system.

    Args:
        port (str): The USB port to validate.

    Raises:
        ValueError: If the specified USB port does not exist.
    """
    if not os.path.exists(port):
        raise ValueError(f"The specified port '{port}' does not exist.")


def main() -> None:
    """
    The main entry point for the Sierra Wireless EM9xxx/EM7xxx CLI tool.

    This function sets up the command-line argument parser, validates the specified
    USB port, and starts the process to query the status of the Sierra Wireless
    module.

    Args:
        None

    Raises:
        ValueError: If the specified USB port does not exist.
        Exception: If any other error occurs during the execution of the tool.
    """
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description="CLI tool for Sierra Wireless EM9xxx/EM7xxx modules to query status",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-p",
        "--port",
        help="USB port to use (e.g., 'COM1' for Windows or '/dev/ttyUSB2' for Linux)",
        required=True,
    )

    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "--version",
        help="Show version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    optional.add_argument(
        "-m",
        "--model",
        help="Model of the device to add to filename (e.g., EM9191 or EM7455)",
        default="",
    )
    optional.add_argument(
        "-v", "--verbose", help="Enable verbose output", action="store_true"
    )
    optional.add_argument(
        "-s", "--search", help="Search for network using AT!COPS=?", action="store_true"
    )
    optional.add_argument(
        "-b",
        "--baudrate",
        help=f"Baudrate to use for serial communication (default: {DEFAULT_BAUDRATE})",
        default=DEFAULT_BAUDRATE,
        type=int,
    )
    optional.add_argument(
        "-i",
        "--interactive",
        help="Enter interactive mode to send custom AT commands",
        action="store_true",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        validate_port(args.port)
        usb_handle.start_process(
            args.port,
            args.model.lower(),
            logging.getLogger().level,
            args.search,
            args.baudrate,
            args.interactive,
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
