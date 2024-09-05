import argparse
import logging
import sys
import os

from sierra_status.__version__ import __version__
from sierra_status.src import usb_handle

DEFAULT_BAUDRATE = 115200

def setup_logging(verbose: bool) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level)

def validate_port(port: str) -> None:
    if not os.path.exists(port):
        raise ValueError(f"The specified port '{port}' does not exist.")

# def validate_port(port: str) -> None:
#     if sys.platform.startswith('win'):
#         # For Windows, we can't easily validate COM ports
#         # We could potentially use the winreg module to check available ports
#         logging.warning("Windows does not have a built-in way to validate COM ports.")
#         pass
#     else:
#         # For Unix-like systems, check if the device file exists
#         if not os.path.exists(port):
#             raise ValueError(f"The specified port '{port}' does not exist.")

def main() -> None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description="CLI tool for Sierra Wireless EM9xxx/EM7xxx modules to query status",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    required = parser.add_argument_group('required arguments')
    required.add_argument("-p", "--port", help="USB port to use (e.g., 'COM1' for Windows or '/dev/ttyUSB2' for Linux)", required=True)
    
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("--version", help="Show version", action="version", version=f"%(prog)s {__version__}")
    optional.add_argument("-m", "--model", help="Model of the device to add to filename (e.g., EM9191 or EM7455)", default="")
    optional.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    optional.add_argument("-s", "--search", help="Search for network using AT!COPS=?", action="store_true")
    optional.add_argument("-b", "--baudrate", help=f"Baudrate to use for serial communication (default: {DEFAULT_BAUDRATE})", default=DEFAULT_BAUDRATE, type=int)
    
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        validate_port(args.port)
        usb_handle.start_process(args.port, args.model.lower(), logging.getLogger().level, args.search, args.baudrate)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
