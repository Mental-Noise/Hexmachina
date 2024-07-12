import asyncio
import board
import digitalio
import json
import storage
import time

from control_change import ControlChange
from led import LED


class Calibration:
    FILE = '/calibration.json'
    DEFAULT_MIN = 0
    DEFAULT_MAX = 26000

    def __init__(self, ccs: list[ControlChange], leds: list[LED]):
        self.ccs = ccs
        self.leds = leds
        self.data = []

    async def start(self):
        button = digitalio.DigitalInOut(board.GP28)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP

        if button.value:
            self.load_calibration()
            return

        await LED.blink_leds(self.leds, 3)
        await asyncio.sleep(1)

        for index, cc in enumerate(self.ccs):
            await LED.blink_led(self.leds[index])
            self.leds[index].low()

            min_val = await self.get_value(button, cc)

            self.leds[index].high()

            max_val = await self.get_value(button, cc)

            self.leds[index].off()
            self.data.append({min: min_val, max: max_val})

        self.save_calibration()

        await LED.blink_leds(self.leds, 5)

    async def get_value(self, button: digitalio.DigitalInOut, cc: ControlChange):
        # Wait for button press
        while button.value:
            await asyncio.sleep(0.0001)

        value = cc.value

        # Wait for button release
        while not button.value:
            await asyncio.sleep(0.0001)

        return value

    def save_calibration(self):
        with storage.open(Calibration.FILE, "w") as f:
            json.dump(self.data, f)

    def load_calibration(self):
        try:
            with storage.open(Calibration.FILE, "r") as f:
                self.data = json.load(f)
        except:
            self.data = [{
                'min': Calibration.DEFAULT_MIN,
                'max': Calibration.DEFAULT_MAX,
            } for _ in self.ccs]