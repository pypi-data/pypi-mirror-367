from ..basefixture import BaseFixture, ColorFixture, StroboFixture


class RootPar6(BaseFixture, ColorFixture, StroboFixture):
    def __init__(self, raw_channel: int | None = None):
        """
        8ch mode
        0 - dimmer
        1 - strobe
        2 - red
        3 - green
        4 - blue
        5 - white
        6 - amber
        7 - uv
        """
        super().__init__(8, raw_channel)
        self._initialize_color_channels(2, 3, 4, 0)
        self._initialize_strobo_channels(1)

    def set_white(self, value: int):
        self.set_value(5, value)

    def set_amber(self, value: int):
        self.set_value(6, value)

    def set_uv(self, value: int):
        self.set_value(7, value)
