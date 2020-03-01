from datetime import datetime
from time import sleep

import RPi.GPIO as GPIO
import asyncio

from sausimat.mfrc522 import MFRC522Sausimat
from sausimat.rotary import Rotary


class Sausimat(MFRC522Sausimat):
    def __init__(self):
        super().__init__()
        self.active_id = None
        self.time_to_stop = 600
        self.detect_interval = 0.1
        self.remove_callback = None
        self.rotary = Rotary(11, 13, 50)

    async def run(self):
        try:
            print("Sausimat Started. Waiting for RFID...")
            check_rifd_task = asyncio.create_task(self.check_rifd())
            #check_volume_task = asyncio.create_task(self.rotary.run(self.set_volume))

            #await check_volume_task
            await check_rifd_task


        except KeyboardInterrupt:
            GPIO.cleanup()
        except:
            pass

    async def check_rifd(self):
        while True:
            id, text = self.read_no_block(remove_callback=self.remove_callback)
            if id and id != self.active_id:
                # new card --> call new card callback
                self.new_card(id, text)
                self.active_id = id
                self.timestamp_on_active = datetime.now()
                self.detect_interval = 2
                self.remove_callback = self.card_removed
            elif id and id == self.active_id:
                # card is still on --> keep reading
                id = None
                self.timestamp_on_active = datetime.now()

            await asyncio.sleep(self.detect_interval)

    def set_volume(self, value):
        print(f"volume: {value}")

    async def check_volume(self):
        while True:
            print('check volume')
            await asyncio.sleep(0.1)

    def new_card(self, id, text):
        print(f"new card: id = {id}, text = {text}")

    def card_removed(self):
        print(f"card removed")
        self.remove_callback = None
        self.active_id = None
        self.detect_interval = 0.1

