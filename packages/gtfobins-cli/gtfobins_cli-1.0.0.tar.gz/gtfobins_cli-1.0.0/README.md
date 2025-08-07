# GTFOBins CLI

[![PyPI version](https://badge.fury.io/py/gtfobins-cli.svg)](https://badge.fury.io/py/gtfobins-cli)
[![Python](https://img.shields.io/pypi/pyversions/gtfobins-cli.svg)](https://pypi.org/project/gtfobins-cli/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build and Publish](https://github.com/t0thkr1s/gtfo/actions/workflows/publish.yml/badge.svg)](https://github.com/t0thkr1s/gtfo/actions/workflows/publish.yml)

## Overview

**GTFOBins CLI** is a command-line interface for [GTFOBins](https://gtfobins.github.io/), providing instant access to Unix binary exploitation techniques. This tool helps security professionals and system administrators identify and understand how legitimate Unix binaries can be misused to bypass security restrictions.

### Key Features

- 🔍 **Quick Binary Lookup**: Search exploitation techniques for any Unix binary
- 🎨 **Syntax Highlighting**: Color-coded output for better readability
- 📦 **Offline Database**: No internet connection required
- 🚀 **Instant Access**: Fast, local searches with zero latency
- 💻 **Cross-Platform**: Works on Linux, macOS, and Windows

## Installation

### From PyPI (Recommended)

```bash
pip install gtfobins-cli
```

### From Source

```bash
git clone https://github.com/t0thkr1s/gtfo
cd gtfo
pip install -e .
```

## Usage

### Basic Usage

```bash
gtfo <binary>
```

### Examples

```bash
# Search for sudo exploitation techniques
gtfo sudo

# Search for python exploitation techniques
gtfo python

# Check version
gtfo --version
```

## Exploitation Categories

The tool provides information about various exploitation techniques:

- **Shell**: Spawn an interactive shell
- **Command**: Execute system commands
- **Reverse Shell**: Establish a reverse shell connection
- **Non-interactive Reverse Shell**: Create a non-interactive reverse shell
- **Bind Shell**: Set up a bind shell
- **Non-interactive Bind Shell**: Create a non-interactive bind shell
- **File Upload**: Transfer files to the target system
- **File Download**: Extract files from the target system
- **File Write**: Write data to files
- **File Read**: Read file contents
- **Library Load**: Load shared libraries
- **SUID**: Exploit SUID permissions
- **Sudo**: Exploit sudo permissions
- **Capabilities**: Exploit Linux capabilities
- **Limited SUID**: Work with limited SUID permissions

## Screenshots

<p align="center">
  <img src="https://i.imgur.com/1EzFiGQ.png" width="45%" alt="GTFOBins CLI Screenshot 1">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://i.imgur.com/icgmDct.png" width="45%" alt="GTFOBins CLI Screenshot 2">
</p>

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/t0thkr1s/gtfo
cd gtfo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

- Binary exploitation data from [GTFOBins](https://gtfobins.github.io/)
- Original GTFOBins project contributors
- Created and maintained by [t0thkr1s](https://github.com/t0thkr1s)

## Security Notice

⚠️ **Important**: This tool is designed for authorized security testing and educational purposes only. Users must:

- Only use this tool on systems they own or have explicit permission to test
- Comply with all applicable laws and regulations
- Understand that misuse of this tool may result in criminal charges

The developers assume no liability and are not responsible for any misuse or damage caused by this tool.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

- Open an [issue](https://github.com/t0thkr1s/gtfo/issues)
- Check existing issues for solutions
- Consult the [GTFOBins website](https://gtfobins.github.io/) for additional information
