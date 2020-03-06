import time
from pyky040 import pyky040
import threading
import RPi.GPIO as GPIO

class Switch:
    PIN_A = 18
    PIN_B = 23
    BOUNCETIME = 500

    def __init__(self, pin_a_board, pin_b_board, initial_value=0):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self):
        GPIO.add_event_detect(self.PIN_A, GPIO.RISING, callback=self.switchA_callback, bouncetime=self.BOUNCETIME)
        GPIO.add_event_detect(self.PIN_B, GPIO.RISING, callback=self.switchB_callback, bouncetime=self.BOUNCETIME)

    def switchA_callback(self, channel):
        print("Switch 18")

    def switchB_callback(self, channel):
        print("Switch 23")


class Rotary:
    def __init__(self, clk, dt, sw, scale_min = 0, scale_max = 100, step = 1):
        self.CLK = clk
        self.DT = dt
        self.SW = sw
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.step = step

        # Init the encoder pins
        self.my_encoder = pyky040.Encoder(CLK=self.CLK, DT=self.DT, SW=self.SW)

        # Or the encoder as a device (must be installed on the system beforehand!)
        # my_encoder = pyky040.Encoder(device='/dev/input/event0')

        # Setup the options and callbacks (see documentation)
        self.my_encoder.setup(scale_min=self.scale_min, scale_max=self.scale_max, step=self.step, chg_callback=self.my_callback)

    def run(self):
        # Create the thread
        my_thread = threading.Thread(target=self.my_encoder.watch)

        # Launch the thread
        my_thread.start()

    def my_callback(self, scale_position):
        print('The scale position is {}'.format(scale_position))
