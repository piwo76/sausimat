import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from time import sleep
import RPi.GPIO as GPIO
from sausimat.mfrc522 import MFRC522Sausimat
from sausimat.rotary import Rotary, Switch
from sausimat.mopidy import SausimatMopidy
import logging


class Sausimat(MFRC522Sausimat):
    def __init__(self):
        super().__init__()
        self.logger = self.create_logger()
        self.logger.info(f'Initializing Sausimat:')
        self.initial_volume = 10
        self.logger.info(f'  PIN_B  = {10}')
        self.active_id = None
        self.time_to_stop = 10
        self.is_pause = False
        self.last_card = None
        self.remove_time = None
        self.detect_interval = 0.1
        self.remove_callback = None
        self.shutdown_card = 77688747180
        self.shutdown_initiated_time = None
        self.time_to_shutdown = 5
        self.rotary = Rotary(17,27,22, initial_counter=self.initial_volume, callback=self.set_volume)
        self.switch = Switch(12,23,500)
        self.mopidy = SausimatMopidy()
        self.mopidy.client.setvol(self.initial_volume)

    def run(self):
        try:
            self.logger.info('Starting Sausimat')
            #check_rifd_task = asyncio.create_task(self.check_rifd())
            #check_volume_task = asyncio.create_task(self.rotary.run(self.set_volume))

            self.rotary.run()
            self.switch.run(self.previous, self.next)

            rfid_thread = threading.Thread(target=self.check_rifd)
            rfid_thread.start()

            check_connection_thread = threading.Thread(target=self.check_connection)
            check_connection_thread.start()

            #await check_rifd_task
            self.logger.info('Sausimat running...')

        except KeyboardInterrupt:
            self.logger.info('Detected keyboard interrupt. Cleaning up...')
            GPIO.cleanup()
        except:
            self.logger.error('Sausimat::run: An unknown error occured')

    def check_rifd(self):
        self.logger.info('Waiting for RFID...')
        while True:
            id, text = self.read_no_block(remove_callback=self.remove_callback)
            if id and id != self.active_id:
                # new card --> call new card callback
                self.new_card(id, text)
                self.active_id = id
                self.detect_interval = 2
                self.remove_callback = self.card_removed
            elif id and id == self.active_id:
                # card is still on --> keep reading
                id = None

            sleep(self.detect_interval)

    def check_connection(self):
        while True:
            self.mopidy.check_connection()
            sleep(10)

    def set_volume(self, value):
        self.logger.info(f'Set volume to {value}')
        self.mopidy.client.setvol(value)

    def get_volume(self):
        self.logger.info(f'Get volume')
        cur_vol = self.mopidy.client.status().get('volume')
        if not cur_vol:
            return self.initial_volume
        self.logger.info(f'current volume: {cur_vol}')
        return cur_vol


    def next(self, channel):
        self.logger.info('Next track')
        self.mopidy.client.next()

    def previous(self, channnel):
        self.logger.info('Previous track')
        self.mopidy.client.previous()

    def new_card(self, id, text):
        try:
            self.logger.info(f'New card detected: id = {id}, text = {text}')
            self.shutdown_initiated_time = None
            if id == self.shutdown_card:
                self.logger.info(f'This is the shutdown card --> Initiating shutdown')
                self.shutdown_initiated_time = datetime.now()
                return

            if self.is_pause and self.last_card == id and (datetime.now()-self.remove_time).total_seconds() < self.time_to_stop:
                self.logger.info(f'Card is paused --> continuing')
                self.mopidy.client.play()
                return

            self.mopidy.play(track='local:track:chrchr.mp3')
            tag_playlist_file = Path(f'/media/playlists/{id}.json')
            self.logger.info(f'tag_playlist_file = {tag_playlist_file}')
            if tag_playlist_file.exists():
                with open(tag_playlist_file) as file:
                    playlist_json = json.load(file)
                    playlist = playlist_json['playlist']
                    self.logger.info(f'playlist = {playlist}')
                    if playlist:
                        volume_gain = playlist_json.get('volume_gain')
                        self.logger.info(f'volume_gain = {volume_gain}')
                        if volume_gain:
                            new_vol = int(self.initial_volume) + int(volume_gain)
                            self.set_volume(new_vol)
                        else:
                            self.set_volume(self.initial_volume)

                        self.mopidy.play(playlist=playlist)
                        self.last_card = id
                        self.is_pause = False
                        self.remove_time = None
            else:
                self.logger.info('tag_playlist_file does not exist')
        except:
            self.logger.error(f'Could not play card with id = {id}')

        print(f"new card: id = {id}, text = {text}")

    def card_removed(self):
        self.logger.info('Card removed')
        if self.shutdown_initiated_time:
            if (datetime.now() - self.shutdown_initiated_time).total_seconds() > self.time_to_shutdown:
                self.logger.info(f'Card was on longer than {self.time_to_shutdown} --> Shutdown!')
                self.mopidy.play(track='local:track:theme2.mp3')
                sleep(4)
                subprocess.run(["sudo", "shutdown"])
                return
            else:
                self.logger.info(f'Card was on shorter than {self.time_to_shutdown} --> Restart!')
                self.mopidy.play(track='local:track:bis_spaeter.mp3')
                sleep(5)
                subprocess.run(["sudo", "reboot"])
                return

        self.remove_callback = None
        self.active_id = None
        self.detect_interval = 0.1
        self.mopidy.client.pause()
        self.is_pause = True
        self.remove_time = datetime.now()

    def create_logger(self):
        logger = logging.getLogger('sausimat')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('/var/log/sausimat.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
