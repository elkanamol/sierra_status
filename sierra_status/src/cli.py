from sierra_status.__version__ import __version__
import argparse
import logging
from sierra_status.src import usb_handle
import sys, os

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
    optional.add_argument("-b", "--baudrate", help="Baudrate to use for serial communication (default: 115200)", default=115200, type=int)
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    usb_handle.start_process(args.port, args.model.lower(), log_level, args.search, args.baudrate)

if __name__ == "__main__":
        main()
    