import logging
from time import sleep

from datetime import datetime
from mpd import MPDClient
import subprocess

class SausimatMopidy:
    def __init__(self):
        self.logger = logging.getLogger('sausimat')
        self.logger.info(f'Initializing Mopidy')
        self.connect()
        self.play(track='local:track:sausimat.mp3')
        

    def connect(self, timeout_sec = 300):
        self.logger.info(f'Connecting to Mopidy...')
        start_time = datetime.now()
        self.client = None
        while not self.client:
            self.client = self.connectMPD()
            if not self.client:
                if timeout_sec and (datetime.now() - start_time).total_seconds() > timeout_sec:
                    self.logger.error(f'Could not connect to mopidy. Please check that the server is running')
                self.logger.info(f'Could not connect to mopidy. Trying again in 2s')
                sleep(2)
        self.logger.info(f'Successfully connected!')

    def check_connection(self):
        try:
            self.client.ping()
        except:
            self.logger.info(f'Reconnecting to MPD...')
            self.connect()

    def rescan_local_library(self):
        self.logger.info(f'Rescan local library...')
        self.logger.info(f'Stopping mopidy...')
        subprocess.run(["sudo", "systemctl", "stop", "mopidy"])
        sleep(5)
        self.logger.info(f'Local scan...')
        subprocess.run(["sudo", "mopidyctl", "local", "scan"])
        sleep(15)
        self.logger.info(f'Starting mopidy...')
        subprocess.run(["sudo", "systemctl", "start", "mopidy"])
        self.connect()

    def play(self, track =None, tracks=None, search_string=None, playlist=None):
        self.logger.info(f'Playing:')
        self.logger.info(f'  track = {track}')
        self.logger.info(f'  nr tracks = {tracks}')
        self.logger.info(f'  search_string = {search_string}')
        self.logger.info(f'  playlist = {playlist}')
        try:
            self.client.stop()
            self.client.clear()
            if tracks and isinstance(tracks, list):
                for track in tracks:
                    self.client.add(track)
            elif track:
                self.client.add(track)
            elif search_string:
                self.client.searchadd('file', search_string)
            elif playlist:
                self.client.load(playlist)

            self.logger.info(f'start playing...')
            self.client.play(0)
        except:
            self.logger.error(f'Could not play the requested tracks')
            sleep(1)
            self.check_connection()

    def create_playlist(self, name, search_string=None, overwrite=False, type='file'):
        self.logger.info(f'Creating playlist:')
        self.logger.info(f'  name = {name}')
        self.logger.info(f'  search_string = {search_string}')
        self.logger.info(f'  overwrite = {overwrite}')
        self.logger.info(f'  type = {type}')
        if overwrite:
            self.client.playlistclear(name)
        else:
            try:
                info = self.client.listplaylistinfo(name)
                self.logger.error(f'The playlist already exists')
                return
            except:
                pass

        if search_string:
            results = self.client.search(type, search_string)
            if not results:
                self.logger.error(f'No tracks found!!')
            if type == 'file':
                for result in results:
                    f = result['file']
                    self.logger.info(f'adding {f}')
                    self.client.playlistadd(name, result['file'])
        self.logger.info(f'playlist created')

    @staticmethod
    def connectMPD():
        logger = logging.getLogger('sausimat')
        try:
            logger.info(f'Connecting to MPD:')
            client = MPDClient()  # create client object
            client.timeout = 200  # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None
            client.connect("localhost", 6600)
            logger.info(f'Successfully connected to MPD')
            return client
        except:
            logger.error(f'Could not connect to MPD')
            return None