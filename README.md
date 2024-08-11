# em-mc_status_script

## Overview

em-mc_status_script is a Python-based CLI tool designed to retrieve and analyze the status of Sierra Wireless EM9xxx,EM7xxx and WP76 modules. This script provides a quick and efficient way to gather essential information from these modules using AT commands.

## Features

- Sends multiple AT commands to query module status
- Supports both EM9xxx and EM7xxx series modules
- Generates a timestamped status file with the collected information
- Optional network search functionality
- Configurable verbosity for debugging

## Installation

To install the package, you can use pip:

```bash
pip install https://github.com/elkanamol/sierra_status.git
```

Alternatively, you can clone the repository and install it locally:

```bash
git clone https://github.com/elkanamol/sierra_status.git 
cd sierra_status 
pip install
```

## Usage

After installation, you can use the `sierra-status` command-line tool:

sierra-status -p [OPTIONS]

### Required Arguments

- `-p, --port`: Specify the USB port to use (e.g., 'COM1' for Windows or '/dev/ttyUSB2' for Linux)

### Optional Arguments

- `-m, --model`: Specify the model of the device to add to the filename (e.g., EM9191 or EM7455)
- `-v, --verbose`: Enable verbose output for debugging
- `-s, --search`: Perform a network search using the AT!COPS=? command
- `--version`: Show the version of the tool

## Key Components

### 1. cli.py

This file contains the main entry point for the CLI tool. It parses command-line arguments and initiates the status retrieval process.

Key functions:

- `main()`: Parses arguments and starts the process

### 2. usb_handle.py

This file contains the core functionality for communicating with the Sierra Wireless modules.

Key functions:

- `send_at_command()`: Sends individual AT commands to the module
- `get_em_status()`: Retrieves the full status by sending multiple AT commands
- `get_em_cops()`: Performs a network search (if enabled)
- `creat_status_file()`: Generates the output file with the collected status information
- `start_process()`: Orchestrates the entire status retrieval process

## AT Commands

The script uses a predefined list of AT commands to query various aspects of the module's status. Some of the key commands include:

- Basic information: ATI, AT+CMEE=1
- Hardware details: AT!HWID?, AT!USBCOMP?, AT!USBSPEED?
- Network status: AT+CREG?, AT+CGREG?, AT+CEREG?
- LTE/NR information: AT!LTEINFO?, AT!NRINFO?

## Output

The script generates a text file with the naming format:

`status_[module_name]_[date].txt`

This file contains the responses from all the AT commands sent to the module, providing a comprehensive snapshot of the module's status.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions to em-mc_status_script are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## Support

For questions or issues, please open an issue on the GitHub repository: <https://github.com/elkanamol/sierra_status/issues>
