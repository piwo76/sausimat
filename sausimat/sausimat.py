import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
import serial
from natsort import natsorted

from sausimat.logger import create_logger
from sausimat.player import Player


class Sausimat():
    def __init__(self, dev='/dev/ttyUSB0', media_dir: str = '/media',  baud_rate=9600, logfile='/var/log/sausimat.log', log_level='INFO', new_card_sound: str = None, startup_sound = None):
        super().__init__()
        self.logger = create_logger('sausimat', logfile, log_level)
        self.logger.info(f'Initializing Sausimat:')
        self.time_to_stop = 10
        self.is_pause = False
        self.last_card = None
        self.remove_time = None
        self.detect_interval = 0.1
        self.ser = serial.Serial(dev, baud_rate, timeout=1)
        self.ser.reset_input_buffer()
        self.media_dir = Path(media_dir)
        self.new_card_sound = str(self.media_dir / 'chrchr.mp3') if not new_card_sound else new_card_sound
        self.startup_sound = str(self.media_dir / 'sausimat.mp3') if not startup_sound else startup_sound
        self.player = Player()
        self.player.play(self.startup_sound, wait=True)

    def run(self):
        try:
            self.logger.info('Starting Sausimat')

            arduino_thread = threading.Thread(target=self.arduino_serial)
            arduino_thread.start()

            self.logger.info('Sausimat running...')

        except KeyboardInterrupt:
            self.logger.info('Detected keyboard interrupt. Cleaning up...')
        except:
            self.logger.error('Sausimat::run: An unknown error occured')

    def perform_action(self, action_str: str):
        try:
            action = json.loads(action_str)
        except:
            self.logger.error(f'could not parse the action: {action_str}')
            return

        if 'arduino' in action:
            self.logger.info(f'arduino successfully connected')
        if 'card' in action:
            uid = action.get('card')
            if uid is None:
                self.card_removed()
            else:
                uid_num = self.uid_to_num(uid)
                if uid_num:
                    self.new_card(uid_num, text=action_str)
        if 'volume' in action:
            volume = action.get('volume')
            if volume is not None:
                self.set_volume(volume)
        if 'button' in action:
            button_nr = action.get('button')
            if button_nr == 0:
                self.previous()
            elif button_nr == 1:
                self.next()
            elif button_nr == 2:
                self.shutdown()
            elif button_nr == 3:
                self.reboot()

    def arduino_serial(self):
        while True:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                self.logger.info(f'New message received from arduino: {line}')
                self.perform_action(line)

    def set_volume(self, value):
        self.logger.info(f'Set volume to {value}')
        self.player.set_volume(value)

    def next(self):
        self.logger.info('Next track')
        self.player.next()

    def previous(self):
        self.logger.info('Previous track')
        self.player.previous()

    def new_card(self, id: int, text: str = None):
        try:
            self.logger.info(f'New card detected: id = {id}, text = {text}')
            if self.is_pause and self.last_card == id and (datetime.now()-self.remove_time).total_seconds() < self.time_to_stop:
                self.logger.info(f'Card is paused --> continuing')
                self.player.unpause()
                self.remove_time = None
                return

            self.player.play(self.new_card_sound, wait=True)

            tag_playlist_file = self.media_dir / f'playlists/{id}.json'
            self.logger.info(f'tag_playlist_file = {tag_playlist_file}')
            if tag_playlist_file.exists():
                with open(tag_playlist_file) as file:
                    playlist_json = json.load(file)
                    folder = playlist_json.get('folder')
                    if folder:
                        folder = self.media_dir / folder
                        if folder.exists():
                            self.logger.info(f'folder = {folder}')
                            playlist = [str(f) for f in natsorted(folder.glob('*.mp3'), key=str)]
                            self.player.play(playlist)
                            self.last_card = id
                            self.is_pause = False
                            self.remove_time = None
            else:
                self.logger.info('tag_playlist_file does not exist')
        except Exception as e:
            self.logger.error(f'Could not play card with id = {id}: {str(e)}')

    def card_removed(self):
        self.logger.info('Card removed')
        self.detect_interval = 0.1
        self.player.pause()
        self.is_pause = True
        self.remove_time = datetime.now()
        check_stop_thread = threading.Thread(target=self.check_for_stop)
        check_stop_thread.start()

    def shutdown(self):
        self.logger.info('Shutdown')
        try:
            subprocess.run(['sudo', 'shutdown', 'now'])
        except:
            pass

    def reboot(self):
        self.logger.info('Reboot')
        try:
            subprocess.run(['sudo', 'reboot'])
        except:
            pass

    def check_for_stop(self):
        time.sleep(self.time_to_stop)
        if self.remove_time is not None:
            self.logger.info(f'card removed longer than {self.time_to_stop}s --> stopping playlist')
            self.player.stop()
            self.remove_time = None
            self.last_card = None

    @staticmethod
    def uid_to_num(uid):
        uid = ''.join(uid.split())
        try:
            return int(uid, 16)
        except:
            return None
