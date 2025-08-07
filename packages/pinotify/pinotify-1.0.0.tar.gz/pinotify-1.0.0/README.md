# Pinotify

[![License][license-badge]][license-url] [![pypi.org][pypi-badge]][pypi-url]

This is a small software for receiving notification of a Raspberry Pi (RPi)
pin change through [libgpiod][libgpiod]. This software monitor the voltage fall
of pin 17. Optionally, this software may run another application through the
`--command` flag.

Initially this was written for hooking a wireless doorbell receiver to an RPi
and then trying to capture electirc signal when the doorbell button is triggered.

The software make use of the new [libgpiod][libgpiod] interface with the
[official Python binding library][libgpiod-python].

[license-badge]: https://img.shields.io/github/license/yookoala/pinotify
[license-url]: https://github.com/yookoala/pinotify/blob/main/LICENSE.md
[pypi-badge]: https://img.shields.io/pypi/v/pinotify
[pypi-url]: https://pypi.org/project/pyinotify/
[libgpiod]: https://libgpiod.readthedocs.io/
[libgpiod-python]: (https://libgpiod.readthedocs.io/en/latest/python_api.html)


## Installation

Clone the repository. Then install the requirements:

```
pip install pinotify
```


## Usage

```
usage: python3 -m pinotify [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--exec COMMAND] [--pin PIN]

Set logging level for the application.

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --exec COMMAND        Command to run when edge event is triggered. In JSON array format.
                        Example: '["echo", "bell rang!"]'.
  --pin PIN             Integer. Set the GPIO pin number to monitor. Default: 17.
```


### Example

Say you want to run "/usr/local/bin/mycommand", with some parameter "param1" and "param2",
whenever a pin 12 voltage drops:

```
python3 -m pinotify --pin 12 --exec '["/usr/local/bin/mycommand", "param1", "param2"]'
```

## Development

### Build as .deb Package

```bash
podman run --volume=".:/opt/pinotify:Z" --workdir="/opt/pinotify" -it docker.io/library/debian:"bookworm" /bin/bash
```

In the docker environment
```bash
apt update
apt install -y build-essential git python3 python3-build python3-setuptools python3-venv python3-all debhelper dh-python
make clean
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
make deb
```


## License

This software is licensed under the [MIT License](https://mit-license.org/).
A copy of the license can be obtained in the repository at [LICENSE.md](LICENSE.md).
