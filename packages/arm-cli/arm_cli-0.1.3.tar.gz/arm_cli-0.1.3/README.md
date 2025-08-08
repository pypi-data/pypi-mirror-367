# arm-cli

[![PyPI](https://img.shields.io/pypi/v/arm-cli.svg)](https://pypi.org/project/arm-cli/)
[![Changelog](https://img.shields.io/github/v/release/mpowelson/arm-cli?include_prereleases&label=changelog)](https://github.com/mpowelson/arm-cli/releases)
[![Tests](https://github.com/mpowelson/arm-cli/actions/workflows/test.yml/badge.svg)](https://github.com/mpowelson/arm-cli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mpowelson/arm-cli/blob/master/LICENSE)

Experimental CLI for deploying robotic applications

## Installation

Install this tool using `pip`:
```bash
pip install arm-cli
```

Once installed, setup the CLI initially by running `arm-cli system setup`. You may need to rerun if you update the CLI via pip. This will do things like configure system settings to enable tab complete.

**Note**: If you installed the CLI with `pip install --user`, you may need to manually run the local bin version the first time:
```bash
~/.local/bin/arm-cli system setup
```

## Usage
### Initial Setup 
For help, run:
```bash
arm-cli --help
```
You can also use:


```bash
python -m arm_cli --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment. From the root of the repo:
```bash
cd arm-cli
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[dev]'
```
To run the tests:
```bash
python -m pytest
```
### Troubleshooting

#### Error: File "setup.py" not found.
If you get this error when running:

> ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: ...
(A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)

it usually means you need to upgrade pip to version 21.3 or newer
```
pip install --upgrade pip
```


