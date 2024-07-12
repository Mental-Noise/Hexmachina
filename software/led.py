import time

from microcontroller import Pin
from pwmio import PWMOut


class LED:
    MAX = 65535

    def __init__(self, pin: Pin):
        self.pwm = PWMOut(pin, frequency=2000, duty_cycle=0)
        self.animation_step = 0
        self.animation_direction = 131
        self.blink_count = 0
        self.blink_last = 0

    def off(self):
        self.pwm.duty_cycle = 0

    def low(self):
        self.pwm.duty_cycle = 1000

    def high(self):
        self.pwm.duty_cycle = LED.MAX

    async def next_animation_frame(self) -> bool:
        if self.animation_step < 0:
            self.pwm.duty_cycle = 0
            return True

        self.pwm.duty_cycle = self.animation_step
        self.animation_step += self.animation_direction

        if self.animation_step > LED.MAX:
            self.animation_direction = -131
            self.animation_step = LED.MAX

        return False

    @staticmethod
    async def animate_led(led: 'LED'):
        return await LED.animate_leds([led])

    @staticmethod
    async def animate_leds(leds: list['LED']):
        i = 1
        start = time.monotonic()
        finished = False

        while True:
            for led in leds[:i]:
                finished = await led.next_animation_frame()

            now = time.monotonic()

            if now - start > 500 and i < len(leds):
                i = i + 1
                start = now

            if finished:
                return

    async def next_blinking_frame(self, bpm: int = 120, count: int = 1) -> bool:
        if self.blink_count >= count:
            self.blink_count = 0
            return True

        if self.blink_last == 0:
            self.blink_last = time.monotonic()
            self.pwm.duty_cycle = LED.MAX

        if time.monotonic() - self.blink_last > 60 / bpm / 2:
            self.blink_last = time.monotonic()

            if self.pwm.duty_cycle == LED.MAX:
                self.pwm.duty_cycle = LED.MIN
            else:
                self.pwm.duty_cycle = LED.MAX
                self.blink_count += 1

        return False

    @staticmethod
    async def blink_led(led: 'LED', count: int = 1):
        return await LED.blink_leds([led], count)

    @staticmethod
    async def blink_leds(leds: list['LED'], count: int = 1):
        finished = False

        while True:
            for led in leds:
                finished = await led.next_blinking_frame(count)

            if finished:
                return
