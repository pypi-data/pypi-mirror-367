from pyftdi.ftdi import Ftdi


def list_devices():
    Ftdi.show_devices()
