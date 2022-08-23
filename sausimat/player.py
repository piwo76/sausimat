import threading
import time
from pathlib import Path
from typing import List, Union

import pygame

from sausimat.logger import create_logger


class Player:
    TRACK_ENDED = pygame.USEREVENT + 1

    def __init__(self, logfile='/var/log/sausimat.log', log_level='INFO'):
        self.logger = create_logger('player', logfile, log_level)
        self.playlist = []
        self.previous_tracks = []
        self.current = None
        self.queue = None
        self._stopped = False
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(self.TRACK_ENDED)  # setup the end track event

    def play(self, tracks: Union[str, List], wait=False):
        self.logger.info('play')
        if isinstance(tracks, str):
            tracks = [tracks]

        tracks = [t for t in tracks if Path(t).exists()]
        self.playlist = tracks

        if wait:
            self.play_playlist()
        else:
            arduino_thread = threading.Thread(target=self.play_playlist)
            arduino_thread.start()

    def pause(self):
        self.logger.info('pause')
        pygame.mixer.music.pause()

    def unpause(self):
        self.logger.info('unpause')
        pygame.mixer.music.unpause()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def stop(self):
        self.logger.info('stop')
        self._stopped = True
        pygame.mixer.music.stop()

    def next(self):
        self.logger.info('next')
        self._set_next()
        self._pygame_play_current()

    def previous(self):
        self.logger.info('previous')
        self._set_previous()
        self._pygame_play_current()

    def play_playlist(self):
        if self.playlist:
            self.logger.info('playing playlist')
            self._init_playlist()
            self._pygame_play_current()
            self._stopped = False

            while not self._stopped:
                for event in self._pygame_get_event():
                    if event.type == self.TRACK_ENDED:  # A track has ended
                        self._set_next()
                        if not self.current:
                            self.stop()

            self.logger.info('playlist stopped')

    def _init_playlist(self):
        self.previous_tracks = []
        self.current = self.playlist.pop(0)
        if len(self.playlist) > 0:
            self.queue = self.playlist.pop(0)

    def _set_next(self):
        self.previous_tracks.append(self.current)
        self.current = self.queue
        if len(self.playlist) > 0:
            self.queue = self.playlist.pop(0)
            self._pygame_set_queue()
        else:
            self.queue = None

    def _set_previous(self):
        if len(self.previous_tracks) > 0:
            if self.queue:
                self.playlist.insert(0, self.queue)
            self.queue = self.current
            self.current = self.previous_tracks.pop()
            self._pygame_set_queue()

    def _pygame_get_event(self):
        return pygame.event.get()

    def _pygame_set_queue(self):
        if self.queue:
            pygame.mixer.music.queue(self.queue)

    def _pygame_play_current(self):
        if self.current:
            pygame.mixer.music.load(self.current)  # Get the first track from the playlist
            if len(self.playlist) > 0:
                pygame.mixer.music.queue(self.queue)  # Queue the 2nd song
            pygame.mixer.music.play()  # Play  = pygame.mixer.music.get()
