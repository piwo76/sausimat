from time import sleep

from datetime import datetime
from mpd import MPDClient
import subprocess

class SausimatMopidy:
    def __init__(self):
        self.connect()
        self.play(track='local:track:sausimat.mp3')
        

    def connect(self, timeout_sec = 60):
        start_time = datetime.now()
        self.client = None
        while not self.client:
            self.client = self.connectMPD()
            if not self.client:
                if timeout_sec and (datetime.now() - start_time).total_seconds() > timeout_sec:
                    raise ValueError('Cannot connect to mopidy. Please check that the server is running')
                sleep(2)

    def rescan_local_library(self):
        subprocess.run(["sudo", "systemctl", "stop", "mopidy"])
        sleep(5)
        subprocess.run(["sudo", "mopidyctl", "local", "scan"])
        subprocess.run(["sudo", "systemctl", "start", "mopidy"])
        self.connect()

    def play(self, track =None, tracks=None, search_string=None, playlist=None):
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

            self.client.play(0)
        except:
            print('Could not play playlist %s' % tracks)

    def create_playlist(self, name, search_string=None, overwrite=False, type='file'):
        if overwrite:
            self.client.playlistclear(name)
        else:
            try:
                info = self.client.listplaylistinfo(name)
                raise ValueError('The playlist already exists')
            except:
                pass

        if search_string:
            results = self.client.search(type, search_string)
            if type == 'file':
                for result in results:
                    self.client.playlistadd(name, result['file'])

    @staticmethod
    def connectMPD():
        try:
            client = MPDClient()  # create client object
            client.timeout = 200  # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None
            client.connect("localhost", 6600)
            return client
        except:
            return None