import adafruit_midi
import board
import busio
import time
import usb_midi
import _thread

from adafruit_ads1x15 import ads1015
from control_change import ControlChange
from led import LED


midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1])
i2c = busio.I2C(sda=board.GP0, scl=board.GP1)

leds = [
    LED(board.GP27),
    LED(board.GP26),
    LED(board.GP2),
    LED(board.GP3),
    LED(board.GP15),
    LED(board.GP14),
    LED(board.GP4),
    LED(board.GP5),
    LED(board.GP10),
    LED(board.GP11),
    LED(board.GP6),
    LED(board.GP7),
    LED(board.GP12),
    LED(board.GP13),
    LED(board.GP8),
    LED(board.GP9),
]

ads = [
    ads1015.ADS1015(i2c, data_rate=3300, address=0x48),
    ads1015.ADS1015(i2c, data_rate=3300, address=0x49),
    ads1015.ADS1015(i2c, data_rate=3300, address=0x4A),
    ads1015.ADS1015(i2c, data_rate=3300, address=0x4B),
]

ccs_core0 = [
    # Row 1
    ControlChange(20, midi, ads[0], ads1015.P0, leds[0]),
    ControlChange(21, midi, ads[0], ads1015.P1, leds[1]),
    ControlChange(22, midi, ads[1], ads1015.P0, leds[2]),
    ControlChange(23, midi, ads[1], ads1015.P1, leds[3]),

    # Row 2
    ControlChange(24, midi, ads[0], ads1015.P2, leds[4]),
    ControlChange(25, midi, ads[0], ads1015.P3, leds[5]),
    ControlChange(26, midi, ads[1], ads1015.P2, leds[6]),
    ControlChange(27, midi, ads[1], ads1015.P3, leds[7]),
]

ccs_core1 = [
    # Row 3
    ControlChange(28, midi, ads[2], ads1015.P0, leds[8]),
    ControlChange(29, midi, ads[2], ads1015.P1, leds[9]),
    ControlChange(30, midi, ads[3], ads1015.P0, leds[10]),
    ControlChange(31, midi, ads[3], ads1015.P1, leds[11]),

    # Row 4
    ControlChange(32, midi, ads[2], ads1015.P2, leds[12]),
    ControlChange(33, midi, ads[2], ads1015.P3, leds[13]),
    ControlChange(34, midi, ads[3], ads1015.P2, leds[14]),
    ControlChange(35, midi, ads[3], ads1015.P3, leds[15]),
]

# Startup animation
i = 1
start = time.time()
finished = False

while True:
    for led in leds[:i]:
        finished = led.next_animation_frame()

    time.sleep(0.001)

    now = time.time()

    if now - start > 1000 and i < 17:
        i = i + 1
        start = now

    if finished:
        time.sleep(1)
        break


# Core 0 handles ADS 1 and 2
def core0_main():
    while True:
        for cc0 in ccs_core0:
            cc0.handle()


# Core 1 handles ADS 3 and 4
def core1_main():
    while True:
        for cc1 in ccs_core1:
            cc1.handle()


_thread.start_new_thread(core0_main, ())
core1_main()