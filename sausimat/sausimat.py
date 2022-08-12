import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from time import sleep
from sausimat.mopidy import SausimatMopidy
import logging
import serial


class Sausimat():
    def __init__(self, dev='/dev/ttyUSB0', baud_rate=9600, logfile='/var/log/sausimat.log', log_level='INFO'):
        super().__init__()
        self.logger = self.create_logger(logfile, log_level)
        self.logger.info(f'Initializing Sausimat:')
        self.initial_volume = 10
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
        self.mopidy = SausimatMopidy()
        self.ser = serial.Serial(dev, baud_rate, timeout=1)
        self.ser.reset_input_buffer()

    def run(self):
        try:
            self.logger.info('Starting Sausimat')

            check_connection_thread = threading.Thread(target=self.check_connection)
            check_connection_thread.start()

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

    def check_connection(self):
        while True:
            self.mopidy.check_connection()
            sleep(10)

    def arduino_serial(self):
        while True:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                self.logger.info(f'New message received from arduino: {line}')
                self.perform_action(line)

    def set_volume(self, value):
        self.logger.info(f'Set volume to {value}')
        if self.mopidy.client:
            self.mopidy.client.setvol(value)

    def get_volume(self):
        self.logger.info(f'Get volume')
        if self.mopidy.client:
            cur_vol = self.mopidy.client.status().get('volume')
            if not cur_vol:
                return self.initial_volume
            self.logger.info(f'current volume: {cur_vol}')
            return cur_vol
        return None


    def next(self):
        self.logger.info('Next track')
        if self.mopidy.client:
            self.mopidy.client.next()

    def previous(self):
        self.logger.info('Previous track')
        if self.mopidy.client:
            self.mopidy.client.previous()

    def new_card(self, id: int, text: str):
        try:
            self.logger.info(f'New card detected: id = {id}, text = {text}')
            self.shutdown_initiated_time = None
            if id == self.shutdown_card:
                self.logger.info(f'This is the shutdown card --> Initiating shutdown')
                self.shutdown_initiated_time = datetime.now()
                return

            if self.is_pause and self.last_card == id and (datetime.now()-self.remove_time).total_seconds() < self.time_to_stop:
                self.logger.info(f'Card is paused --> continuing')
                if self.mopidy.client:
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
        if self.mopidy.client:
            self.mopidy.client.pause()
        self.is_pause = True
        self.remove_time = datetime.now()

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

    def create_logger(self, logfile_path: str, log_level: str):
        level = logging.getLevelName(log_level)
        do_logfile = True
        if not Path(logfile_path).parent.exists():
            do_logfile = False

        logging.basicConfig(level=logging.NOTSET)
        logger = logging.getLogger('sausimat')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if do_logfile:
            fh = logging.FileHandler(logfile_path)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    @staticmethod
    def uid_to_num(uid):
        uid = ''.join(uid.split())
        try:
            return int(uid, 16)
        except:
            return None
