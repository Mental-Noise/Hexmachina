import asyncio
from calendar import prcal

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_midi import MIDI
from adafruit_midi.control_change import ControlChange as MidiControlChange
from led import LED


class ControlChange:
    CHANGE_THRESHOLD = 50

    def __init__(self, cc: int, midi: MIDI, ads: ADS1015, ads_pin: int, led: LED):
        self.cc = cc
        self.midi = midi
        self.chan = AnalogIn(ads, ads_pin)
        self.led = led

        self.last_value = 0
        self.last_cc_value = 0

    @property
    def value(self):
        return self.chan.value

    async def handle(self, calibration_data):
        value = self.value

        if abs(value - self.last_value) < ControlChange.CHANGE_THRESHOLD:
            return

        self.last_value = value
        self.set_led_brightness(value, calibration_data.min, calibration_data.max)
        self.send_midi_cc(value, calibration_data.min, calibration_data.max)

        await asyncio.sleep(0.0001)

    def set_led_brightness(self, value, min_value, max_value):
        self.led.pwm.duty_cycle = ControlChange.map(value, min_value, max_value, 0, 65535)

    def send_midi_cc(self, value,  min_value, max_value):
        cc_value = ControlChange.map(value,  min_value, max_value, 0, 127)

        if cc_value == self.last_cc_value:
            return

        self.midi.send(MidiControlChange(self.cc, cc_value))
        self.last_cc_value = cc_value

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
