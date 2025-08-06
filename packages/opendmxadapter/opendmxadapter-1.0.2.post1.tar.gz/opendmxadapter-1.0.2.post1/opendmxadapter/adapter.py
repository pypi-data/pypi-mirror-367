import sys
import time
import threading

import pyftdi.serialext
from serial import serialutil

from . import fixtures


class OpenDMXAdapter:
    def __init__(self, serial_port: str):
        """
        Initializes the OpenDMXAdapter with the specified serial port.
        Use utils.helper.list_devices() to find the correct serial uri.

        :param serial_port: Something like "ftdi://ftdi:232:BG00DND8/1"
        """
        self.is_connected = False

        try:
            self.serial = pyftdi.serialext.serial_for_url(serial_port, baudrate=250000, stopbits=2)
        except ValueError as e:
            print("Malformed serialPort url: " + serial_port)
            print(e)
            sys.exit(0)
        except serialutil.SerialException as e:
            print("Error: could not open Serial Port")
            print(e)
            sys.exit(0)

        self.is_connected = True
        self.dmx_data = [bytes([0])] * 513
        self.dmx_data[0] = bytes([0])
        self.display_thread = threading.Thread(target=self._display_universe)
        self.fixtures = []
        self.channel_index = 0

    def add_fixture(self, fixture: 'fixtures.basefixture.BaseFixture') -> None:
        """
        Adds a fixture to the DMX adapter which will be initialized with the next available channel index.
        :param fixture: An instance of a fixture that inherits from BaseFixture.
        :return: None
        """
        fixture.adapter = self
        self.channel_index += fixture.initialize(self.channel_index)

        if self.channel_index > len(self.dmx_data) - 1:
            raise RuntimeError("Channel index out of range")

        self.fixtures.append(fixture)

    def add_fixtures(self, *fixture_list: 'fixtures.basefixture.BaseFixture') -> None:
        """
        Adds multiple fixtures to the DMX adapter.
        :param fixture_list: A variable number of fixture instances that inherit from BaseFixture.
        :return: None
        """
        for fixture in fixture_list:
            self.add_fixture(fixture)

    def set_channel(self, channel, intensity) -> None:
        """
        Sets the intensity for a specific DMX channel.

        :param channel: The DMX channel number (0-512).
        :param intensity: The intensity value (0-255) to set for the channel.
        :return: None
        """
        channel = max(0, min(512, channel))
        intensity = max(0, min(255, intensity))
        self.dmx_data[channel + 1] = bytes([intensity])

    def blackout(self) -> None:
        """
        Sets all DMX channels to zero intensity, effectively blacking out the output.
        :return: None
        """
        for i in range(1, 512, 1):
            self.dmx_data[i] = bytes([0])

    def start(self) -> None:
        """
        Starts the display thread that continuously renders the DMX universe.
        :return: None
        """
        self.display_thread.start()

    def close(self):
        """
        Closes the serial connection and stops the display thread.
        :return: None
        """
        self.is_connected = False
        self.display_thread.join()
        self.serial.close()

    def _display_universe(self):
        while self.is_connected:
            self._render()
            time.sleep(8 / 1000.0)  # 40 Hz for Enttec Open DMX USB

    def _render(self):
        if not self.is_connected:
            return

        sdata = b''.join(self.dmx_data)
        self.serial.send_break(duration=0.001)
        self.serial.write(sdata)


# Guide to install driver: https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/windows
if __name__ == '__main__':
    url = "ftdi://ftdi:232:BG00DND8/1"

    dmx = OpenDMXAdapter(url)
    dmx.start()

    dmx.set_channel(1, 200)
    dmx.set_channel(3, 100)

    print("Start fading...")

    for i in range(0, 255):
        print(f"\r{int((i / 255) * 100)}% done", end='')
        dmx.set_channel(4, i)
        time.sleep(0.01)

    print("\nFading done.")
    time.sleep(5)

    print("Blackout")
    dmx.blackout()

    time.sleep(1)
    dmx.close()

