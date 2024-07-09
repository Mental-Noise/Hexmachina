import supervisor
import usb_midi

supervisor.set_usb_identification(manufacturer="Mental Noise", product="Hexmachina")
usb_midi.ports[1].name = "Hexmachina"