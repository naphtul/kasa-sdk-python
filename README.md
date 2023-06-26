# Kasa SDK implementation
A simple implementation of Python SDK for Kasa (tp-link) to interact with Kasa's smart devices to run simple operations and get information.

## Setup
This package requires to run on the local network where the devices are located.

## Usage
```python
import Kasa

kasa = Kasa()
device_list = kasa.discover_devices()
kasa.toggle('Office')
```