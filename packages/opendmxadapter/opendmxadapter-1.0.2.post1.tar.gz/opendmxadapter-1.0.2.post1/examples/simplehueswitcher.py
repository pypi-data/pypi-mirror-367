import time

import colorsys

from adapter import OpenDMXAdapter
from fixtures.cameo.rootpar6 import RootPar6

controller = OpenDMXAdapter("ftdi://ftdi:232:BG00DND8/1")
controller.start()
controller.blackout()

light = RootPar6(0)
controller.add_fixture(light)


for i in range(361):
    r, g, b = colorsys.hsv_to_rgb(i / 360, 1, 1)
    print(f"\r{r}/{g}/{b}", end="")
    light.set_rgb(int(r * 255), int(g * 255), int(b * 255))
    time.sleep(0.01)

print("\nDone!")
