# Raspberry

## Requirements

* Python 3+

## Installation

Installation

```sh
$ virtualenv3 venv
$ . ./venv/bin/activate
$ pip3 install paho-mqtt tinkerforge
```

Systemd unit `/etc/systemd/system/dapo.service`:
```
[Unit]
Description=dapo
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/raspberry/gateway.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
