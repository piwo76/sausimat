import threading
import time
from pathlib import Path

from sausimat.player import Player
from mock import patch

from sausimat.sausimat import Sausimat

track_list = []

def play(self, track_len):
    time.sleep(track_len)
    self.stop()


def play_current(self):
    self.stop()
    name = Path(self.current).name
    track_list.append(name)
    track_len = 60
    if name == 'chrchr.mp3':
        track_len = 2
    if name == 'sausimat.mp3':
        track_len = 2

    play_thread = threading.Thread(target=play, args=(self, track_len))
    play_thread.start()


class TestSausimat:
    def test_init(self):
        global track_list
        media_dir = str((Path(__file__).parent / 'media').resolve())
        track_list = []
        with patch('serial.Serial'):
            with patch.object(Player, '_pygame_play_current', play_current) as mock_func:
                sausimat = Sausimat(media_dir=media_dir)
                sausimat.new_card(id=1714214787)

                time.sleep(5)
                sausimat.next()

                time.sleep(5)
                sausimat.next()

                time.sleep(5)
                sausimat.previous()

                time.sleep(5)
                sausimat.previous()

                time.sleep(5)
                sausimat.previous()

                time.sleep(5)
                sausimat.card_removed()

                time.sleep(2)
                sausimat.new_card(id=1714214787)

                time.sleep(5)
                sausimat.card_removed()

                assert len(track_list) == 8
                assert track_list[0] == 'sausimat.mp3'
                assert track_list[1] == 'chrchr.mp3'
                assert track_list[2] == '01.mp3'
                assert track_list[3] == '02.mp3'
                assert track_list[4] == '03.mp3'
                assert track_list[5] == '02.mp3'
                assert track_list[6] == '01.mp3'
                assert track_list[7] == '01.mp3'
