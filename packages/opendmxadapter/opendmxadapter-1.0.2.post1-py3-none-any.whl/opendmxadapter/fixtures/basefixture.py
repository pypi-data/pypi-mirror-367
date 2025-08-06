from ..adapter import OpenDMXAdapter


class _AbstractFixture:
    adapter: OpenDMXAdapter

    def initialize(self, channel_index: int):
        ...

    def set_value(self, index: int, value: int):
        ...


class BaseFixture(_AbstractFixture):
    def __init__(self,
                 channel_count: int,
                 raw_channel: int | None = None):
        self.raw_channel = raw_channel
        self.channel_count = channel_count
        self.auto_calculate_channel = self.raw_channel is None

    def initialize(self, channel_index: int):
        if self.auto_calculate_channel:
            self.raw_channel = channel_index

        # Black out everything
        for i in range(self.channel_count):
            self.set_value(i, 0)

        return self.channel_count

    def set_value(self, index: int, value: int):
        if not isinstance(index, int):
            raise TypeError('index must be an integer')

        if not isinstance(value, int):
            raise TypeError('value must be an int')

        if index < 0 or index >= self.channel_count:
            raise IndexError

        value = min(255, max(0, int(value)))
        self.adapter.set_channel(self.raw_channel + index, value)


class ColorFixture(_AbstractFixture):
    _redChannel: int | None = None
    _greenChannel: int | None = None
    _blueChannel: int | None = None
    _intensityChannel: int | None = None

    def _initialize_color_channels(self, red_channel: int, green_channel: int, blue_channel: int,
                                   intensity_channel: int | None):
        self._redChannel = red_channel
        self._greenChannel = green_channel
        self._blueChannel = blue_channel
        self._intensityChannel = intensity_channel

    def set_rgb(self, r: int, g: int, b: int):
        self.set_value(self._redChannel, r)
        self.set_value(self._greenChannel, g)
        self.set_value(self._blueChannel, b)

    def set_intensity(self, intensity: int):
        self.set_value(self._intensityChannel, intensity)


class StroboFixture(_AbstractFixture):
    _stroboChannel: int | None = None

    def _initialize_strobo_channels(self, strobo_channel):
        self._stroboChannel = strobo_channel

    def set_strobo(self, value: int):
        self.set_value(self._stroboChannel, value)


class MovingHeadFixture(_AbstractFixture):
    _pan_channel: int | None = None
    _pan_fine_channel: int | None = None
    _tilt_channel: int | None = None
    _tilt_fine_channel: int | None = None
    _moving_speed_channel: int | None = None

    def _initialize_moving_head_channels(self, pan_channel: int, pan_fine_channel: int | None, tilt_channel: int,
                                         tilt_fine_channel: int | None, moving_speed_channel: int | None):
        self._pan_channel = pan_channel
        self._pan_fine_channel = pan_fine_channel
        self._tilt_channel = tilt_channel
        self._tilt_fine_channel = tilt_fine_channel
        self._moving_speed_channel = moving_speed_channel

    def set_pan(self, value: int):
        self.set_value(self._pan_channel, value)

    def set_pan_fine(self, value: int):
        self.set_value(self._pan_fine_channel, value)

    def set_tilt(self, value: int):
        self.set_value(self._tilt_channel, value)

    def set_tilt_fine(self, value: int):
        self.set_value(self._tilt_fine_channel, value)

    def set_moving_speed(self, speed: int):
        self.set_value(self._moving_speed_channel, speed)
