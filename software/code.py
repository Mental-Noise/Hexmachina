import adafruit_midi
import asyncio
import board
import busio
import usb_midi

from adafruit_ads1x15 import ads1015
from control_change import ControlChange
from led import LED
from software.calibration import Calibration

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1])
i2c = busio.I2C(sda=board.GP0, scl=board.GP1)

leds = [
    LED(board.GP27), LED(board.GP26), LED(board.GP2), LED(board.GP3),
    LED(board.GP15), LED(board.GP14), LED(board.GP4), LED(board.GP5),
    LED(board.GP10), LED(board.GP11), LED(board.GP6), LED(board.GP7),
    LED(board.GP12), LED(board.GP13), LED(board.GP8), LED(board.GP9),
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

calibration = Calibration(ccs_core0 + ccs_core1, leds)


async def handle_ccs(ccs: list[ControlChange], calibration_data):
    while True:
        for index, cc in enumerate(ccs):
            await cc.handle(calibration_data[index])


async def main():
    await LED.animate_leds(leds)
    await calibration.start()
    task1 = asyncio.create_task(handle_ccs(ccs_core0, calibration.data))
    task2 = asyncio.create_task(handle_ccs(ccs_core1, calibration.data))
    await asyncio.gather(task1, task2)


# Run the main function
asyncio.run(main())
