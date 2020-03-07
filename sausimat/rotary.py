import logging
import time
from pyky040 import pyky040
import threading
import RPi.GPIO as GPIO

class Switch:
    def __init__(self, pin_a, pin_b, bouncetime = 500):
        self.logger = logging.getLogger('sausimat')
        self.logger.info(f'Initializing 3-way switch:')
        self.logger.info(f'  PIN_A = {pin_a}')
        self.logger.info(f'  PIN_B  = {pin_b}')
        self.logger.info(f'  BOUNCETIME  = {bouncetime}')
        self.PIN_A = pin_a
        self.PIN_B = pin_b
        self.BOUNCETIME = bouncetime
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self, callback_a = None, callback_b = None):
        GPIO.add_event_detect(self.PIN_A, GPIO.RISING, callback=callback_a, bouncetime=self.BOUNCETIME)
        GPIO.add_event_detect(self.PIN_B, GPIO.RISING, callback=callback_b, bouncetime=self.BOUNCETIME)
        self.logger.info(f'Switch started and listening...')


class Rotary:
    def __init__(self, clk, dt, sw, initial_counter = 0, scale_min = 0, scale_max = 100, step = 1, callback=None):
        self.logger = logging.getLogger('sausimat')
        self.logger.info(f'Initializing rotary:')
        self.logger.info(f'  CLK = {clk}')
        self.logger.info(f'  CT  = {dt}')
        self.logger.info(f'  SW  = {sw}')
        self.logger.info(f'  scale_min  = {scale_min}')
        self.logger.info(f'  scale_max  = {scale_max}')
        self.logger.info(f'  step  = {step}')
        self.logger.info(f'  initial value  = {initial_counter}')
        self.CLK = clk
        self.DT = dt
        self.SW = sw
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.step = step
        self.initial_value = initial_counter

        # Init the encoder pins
        self.my_encoder = pyky040.Encoder(CLK=self.CLK, DT=self.DT, SW=self.SW)

        # Or the encoder as a device (must be installed on the system beforehand!)
        # my_encoder = pyky040.Encoder(device='/dev/input/event0')

        # Setup the options and callbacks (see documentation)
        self.my_encoder.setup(scale_min=self.scale_min, scale_max=self.scale_max, step=self.step, chg_callback=callback)
        self.my_encoder.counter = self.initial_value

    def run(self):
        # Create the thread
        my_thread = threading.Thread(target=self.my_encoder.watch)

        # Launch the thread
        my_thread.start()
        self.logger.info(f'Rotary started and listening...')
