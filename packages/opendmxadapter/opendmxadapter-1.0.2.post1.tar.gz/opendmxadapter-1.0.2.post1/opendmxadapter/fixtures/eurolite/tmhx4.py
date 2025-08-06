from ..basefixture import BaseFixture, ColorFixture, MovingHeadFixture, StroboFixture


class TMHX4(BaseFixture, ColorFixture, MovingHeadFixture, StroboFixture):
    def __init__(self, raw_channel: int | None = None):
        """
        16ch mode
        ...

        24ch mode
        0 - Pan Clockwise
        1 - Pan fine
        2 - Tilt
        3 - Tilt fine
        4 - Moving Speed (1-212: less speed, 213-255: nothing)
        5 - Lens Zoom
        6 - Intensity
        7 - Strobo (0-3: None, 4-95: normal, 96-176: random, 177-255: "thunder"-strobe)

        8 - Red     Inner
        9 - Green   Inner
        10 - Blue   Inner
        11 - White  Inner

        12 - Red    Outer (Top-Start)
        13 - Green  Outer (Top-Start)
        14 - Blue   Outer (Top-Start)
        15 - White  Outer (Top-Start)

        16 - Red    Outer (Non-Top-Start)
        17 - Green  Outer (Non-Top-Start)
        18 - Blue   Outer (Non-Top-Start)
        19 - White  Outer (Non-Top-Start)

        20 - Color Preset and Macro
        21 - Macro Speed
        22 - Pattern (0-49: Channel 1-20, 50-99: Presets/Macros, 100-149: Internal P1, 150-199: Internal P2, 200-255: Music)
        23 - Reset (251-255)
        """
        super().__init__(24, raw_channel)
        self._initialize_color_channels(8, 9, 10, 6)
        self._initialize_moving_head_channels(0, 1, 2, 3, 4)
        self._initialize_strobo_channels(7)

    def set_outer_color(self, r: int, g: int, b: int, w: int, top_start: bool = True):
        self.set_value(12 + 4 if top_start else 0, r)
        self.set_value(13 + 4 if top_start else 0, g)
        self.set_value(14 + 4 if top_start else 0, b)
        self.set_value(15 + 4 if top_start else 0, w)

    def set_lens_zoom(self, value: int):
        self.set_value(5, value)

    def set_pattern(self, value: int):
        self.set_value(22, value)

    def set_reset(self, should_reset: bool):
        self.set_value(23, 255 if should_reset else 0)

    def set_color_macro(self, value: int):
        self.set_value(20, value)

    def set_macro_speed(self, value: int):
        self.set_value(21, value)
