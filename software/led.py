from microcontroller import Pin
from pwmio import PWMOut


class LED:
    def __init__(self, pin: Pin):
        self.pwm = PWMOut(pin, frequency=2000, duty_cycle=0)
        self.animation_step = 0
        self.animation_direction = 1

    def next_animation_frame(self) -> bool:
        if self.animation_step < 0:
            return True

        self.pwm.duty_cycle = self.animation_step
        self.animation_step += self.animation_direction

        if self.animation_step > 65535:
            self.animation_direction = -1
            self.animation_step = 65534

        return False
