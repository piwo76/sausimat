from sausimat.player import Player
from mock import patch


class TestPlayer:
    def test_next(self):
        with patch('sausimat.player.Player._pygame_play_current'):
            with patch('sausimat.player.Player._pygame_set_queue'):
                playlist = [str(i) for i in range(2, 10)]
                player = Player()
                player.playlist = playlist
                player.current = '0'
                player.queue = '1'

                player.next()

                assert player.current == '1'
                assert player.queue == '2'
                assert player.playlist == [str(i) for i in range(3, 10)]
                assert player.previous_tracks == ['0']

                player.next()
                assert player.current == '2'
                assert player.queue == '3'
                assert player.playlist == [str(i) for i in range(4, 10)]
                assert player.previous_tracks == ['0', '1']

    def test_previous(self):
        with patch('sausimat.player.Player._pygame_play_current'):
            with patch('sausimat.player.Player._pygame_set_queue'):
                playlist = [str(i) for i in range(4, 10)]
                player = Player()
                player.playlist = playlist
                player.current = '2'
                player.queue = '3'
                player.previous_tracks = ['0', '1']

                player.previous()
                assert player.current == '1'
                assert player.queue == '2'
                assert player.playlist == [str(i) for i in range(3, 10)]
                assert player.previous_tracks == ['0']

                player.previous()
                assert player.current == '0'
                assert player.queue == '1'
                assert player.playlist == [str(i) for i in range(2, 10)]
                assert player.previous_tracks == []

                player.previous()
                assert player.current == '0'
                assert player.queue == '1'
                assert player.playlist == [str(i) for i in range(2, 10)]
                assert player.previous_tracks == []

